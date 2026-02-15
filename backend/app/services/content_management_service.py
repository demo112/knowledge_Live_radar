import re
import logging
import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.content import ContentItem, ValidationResult, ContentNodeRelation
from app.schemas.content_management import BatchCleanData, CleanDetail, BatchDeleteData, BatchSummarizeData
from app.services.ai_service import ai_service
from app.services.validator.soft_validator import SoftValidator

logger = logging.getLogger(__name__)

class ContentManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.soft_validator = SoftValidator()

    def _calculate_chinese_ratio(self, text: str) -> float:
        """Calculate the ratio of Chinese characters in the text."""
        if not text:
            return 0.0
        # Remove whitespace to get a more accurate content ratio
        clean_text = re.sub(r'\s+', '', text)
        if not clean_text:
            return 0.0
            
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', clean_text)
        return len(chinese_chars) / len(clean_text)

    async def batch_clean(self, dry_run: bool = False, chinese_ratio_threshold: float = 0.2) -> BatchCleanData:
        """
        Clean content based on:
        1. Chinese character ratio (must be >= threshold)
        2. AI relevance check (must be relevant to AI/Tech)
        """
        stmt = select(ContentItem)
        result = await self.db.execute(stmt)
        all_items = result.scalars().all()
        
        total_scanned = len(all_items)
        items_to_delete: List[CleanDetail] = []
        
        import asyncio
        # Use semaphore to limit concurrent AI calls
        semaphore = asyncio.Semaphore(10)

        async def check_item(item):
            async with semaphore:
                try:
                    # 1. Check Chinese Ratio
                    # Combine title and content for better context
                    full_text = f"{item.title} {item.content_text or ''}"
                    ratio = self._calculate_chinese_ratio(full_text)
                    
                    if ratio < chinese_ratio_threshold:
                        return CleanDetail(
                            id=str(item.id),
                            title=item.title,
                            reason=f"Low Chinese ratio: {ratio:.2f} < {chinese_ratio_threshold}"
                        )
                        
                    # 2. Check AI Relevance (Soft Validation)
                    # Only check if it passed the language check
                    item_dict = {
                        "title": item.title,
                        "content": item.content_text
                    }
                    
                    # Use SoftValidator logic
                    is_valid, details = await self.soft_validator.validate(item_dict)
                    
                    if not is_valid:
                        score = details.get("score", 0)
                        reason = details.get("reason", "Unknown")
                        return CleanDetail(
                            id=str(item.id),
                            title=item.title,
                            reason=f"Irrelevant content (Score: {score}): {reason}"
                        )
                except Exception as e:
                    logger.error(f"Check failed for item {item.id}: {e}")
                    # Optionally skip or count as valid to avoid accidental deletion
                return None

        try:
            # Run checks in parallel
            results = await asyncio.gather(*[check_item(item) for item in all_items])
            items_to_delete = [r for r in results if r is not None]
            
            deleted_count = len(items_to_delete)
            
            if not dry_run and items_to_delete:
                # Convert string IDs back to UUIDs if necessary, but sqlalchemy usually handles it.
                # To be safe, we rely on the fact that CleanDetail.id is a string representation of the UUID.
                delete_ids = [uuid.UUID(item.id) for item in items_to_delete]
                
                # Delete logic
                # 1. Delete ValidationResults
                await self.db.execute(
                    delete(ValidationResult).where(ValidationResult.content_id.in_(delete_ids))
                )
                # 2. Delete ContentNodeRelations (Cascade should handle, but explicit is safer if not configured)
                await self.db.execute(
                    delete(ContentNodeRelation).where(ContentNodeRelation.content_id.in_(delete_ids))
                )
                # 3. Delete ContentItems
                await self.db.execute(
                    delete(ContentItem).where(ContentItem.id.in_(delete_ids))
                )
                await self.db.commit()
                
            return BatchCleanData(
                total_scanned=total_scanned,
                deleted_count=deleted_count,
                details=items_to_delete
            )
        except Exception as e:
            logger.error(f"Batch clean failed: {e}", exc_info=True)
            raise

    async def batch_delete(self, ids: List[uuid.UUID]) -> BatchDeleteData:
        """Batch delete content items by ID."""
        if not ids:
            return BatchDeleteData(deleted_count=0)
            
        # 1. Delete ValidationResults
        await self.db.execute(
            delete(ValidationResult).where(ValidationResult.content_id.in_(ids))
        )
        # 2. Delete ContentNodeRelations
        await self.db.execute(
            delete(ContentNodeRelation).where(ContentNodeRelation.content_id.in_(ids))
        )
        # 3. Delete ContentItems
        result = await self.db.execute(
            delete(ContentItem).where(ContentItem.id.in_(ids))
        )
        await self.db.commit()
        
        return BatchDeleteData(deleted_count=result.rowcount)

    async def batch_summarize(self, target_ids: Optional[List[uuid.UUID]] = None, overwrite: bool = True) -> BatchSummarizeData:
        """
        Trigger batch summarization.
        This method will be called by the router to start a background task.
        """
        # Count items to be processed
        stmt = select(ContentItem)
        if target_ids:
            stmt = stmt.where(ContentItem.id.in_(target_ids))
        
        if not overwrite:
            stmt = stmt.where(ContentItem.summary == None)
            
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        return BatchSummarizeData(
            task_id="async-task-started",
            message=f"Summarization started for {len(items)} items."
        )

async def run_batch_summarization(target_ids: Optional[List[uuid.UUID]] = None, overwrite: bool = True):
    """
    Background task to process summarization.
    """
    from app.database import AsyncSessionLocal
    
    logger.info(f"Starting batch summarization task. Target IDs: {len(target_ids) if target_ids else 'ALL'}, Overwrite: {overwrite}")
    
    async with AsyncSessionLocal() as db:
        stmt = select(ContentItem)
        if target_ids:
            stmt = stmt.where(ContentItem.id.in_(target_ids))
        
        # If not overwrite, filter out items that already have summary
        if not overwrite:
            stmt = stmt.where(ContentItem.summary == None)
            
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        processed_count = 0
        failed_count = 0
        
        for item in items:
            try:
                # Generate summary
                # ai_service.generate_summary returns a dict with "summary" key
                result = await ai_service.generate_summary(item.title, item.content_text or "")
                summary = result.get("summary")
                
                if summary:
                    item.summary = summary
                    item.ai_processed = True
                    processed_count += 1
                    # Commit every item to avoid long transaction and save progress
                    await db.commit()
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to summarize item {item.id}: {e}")
                failed_count += 1
                
        logger.info(f"Batch summarization completed. Processed: {processed_count}, Failed: {failed_count}")
