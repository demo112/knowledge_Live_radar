import re
import logging
import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.content import ContentItem, ValidationResult, ContentNodeRelation
from app.schemas.content_management import BatchCleanData, CleanDetail, BatchDeleteData, BatchSummarizeData
from app.core.ai.facade import ai_facade
from app.services.validator.soft_validator import SoftValidator

logger = logging.getLogger(__name__)

class ContentManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.soft_validator = SoftValidator()

    def _calculate_chinese_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        clean_text = re.sub(r'\s+', '', text)
        if not clean_text:
            return 0.0
            
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', clean_text)
        return len(chinese_chars) / len(clean_text)

    async def batch_clean(self, dry_run: bool = False, chinese_ratio_threshold: float = 0.2) -> BatchCleanData:
        stmt = select(ContentItem)
        result = await self.db.execute(stmt)
        all_items = result.scalars().all()
        
        total_scanned = len(all_items)
        items_to_delete: List[CleanDetail] = []
        
        import asyncio
        semaphore = asyncio.Semaphore(10)

        async def check_item(item):
            async with semaphore:
                try:
                    full_text = f"{item.title} {item.content_text or ''}"
                    ratio = self._calculate_chinese_ratio(full_text)
                    
                    if ratio < chinese_ratio_threshold:
                        return CleanDetail(
                            id=str(item.id),
                            title=item.title,
                            reason=f"Low Chinese ratio: {ratio:.2f} < {chinese_ratio_threshold}"
                        )
                        
                    item_dict = {
                        "title": item.title,
                        "content": item.content_text
                    }
                    
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
                return None

        try:
            results = await asyncio.gather(*[check_item(item) for item in all_items])
            items_to_delete = [r for r in results if r is not None]
            
            deleted_count = len(items_to_delete)
            
            if not dry_run and items_to_delete:
                delete_ids = [uuid.UUID(item.id) for item in items_to_delete]
                
                await self.db.execute(
                    delete(ValidationResult).where(ValidationResult.content_id.in_(delete_ids))
                )
                await self.db.execute(
                    delete(ContentNodeRelation).where(ContentNodeRelation.content_id.in_(delete_ids))
                )
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
        if not ids:
            return BatchDeleteData(deleted_count=0)
            
        await self.db.execute(
            delete(ValidationResult).where(ValidationResult.content_id.in_(ids))
        )
        await self.db.execute(
            delete(ContentNodeRelation).where(ContentNodeRelation.content_id.in_(ids))
        )
        result = await self.db.execute(
            delete(ContentItem).where(ContentItem.id.in_(ids))
        )
        await self.db.commit()
        
        return BatchDeleteData(deleted_count=result.rowcount)

    async def batch_summarize(self, target_ids: Optional[List[uuid.UUID]] = None, overwrite: bool = True) -> BatchSummarizeData:
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
    from app.database import AsyncSessionLocal
    
    logger.info(f"Starting batch summarization task. Target IDs: {len(target_ids) if target_ids else 'ALL'}, Overwrite: {overwrite}")
    
    async with AsyncSessionLocal() as db:
        stmt = select(ContentItem)
        if target_ids:
            stmt = stmt.where(ContentItem.id.in_(target_ids))
        
        if not overwrite:
            stmt = stmt.where(ContentItem.summary == None)
            
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        processed_count = 0
        failed_count = 0
        
        for item in items:
            try:
                result = await ai_facade.generate_summary(item.title, item.content_text or "")
                summary = result.get("summary")
                
                if summary:
                    item.summary = summary
                    item.ai_processed = True
                    processed_count += 1
                    await db.commit()
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to summarize item {item.id}: {e}")
                failed_count += 1
                
        logger.info(f"Batch summarization completed. Processed: {processed_count}, Failed: {failed_count}")
