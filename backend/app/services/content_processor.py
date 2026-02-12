from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crawl_engine import crawl_engine
from app.services.validator import HardValidator, SoftValidator, CrossValidator
from app.models.source import InformationSource
from app.models.content import ContentItem, ValidationResult
from app.models.crawl_job import CrawlJob
from typing import List
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ContentProcessor:
    async def process_source(self, source: InformationSource, session: AsyncSession) -> CrawlJob:
        """
        Process a source: fetch, validate, save.
        """
        # Create job record
        job = CrawlJob(
            source_id=source.id, 
            status="RUNNING",
            started_at=datetime.now(timezone.utc)
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        
        try:
            # 1. Fetch
            items = await crawl_engine.crawl_source(source)
            job.items_fetched = len(items)
            
            # Initialize validators
            hard_validator = HardValidator()
            soft_validator = SoftValidator()
            cross_validator = CrossValidator(session)
            
            new_items_count = 0
            failed_count = 0
            duplicate_count = 0
            
            for item_data in items:
                # 2. Validation
                
                # Cross Validation (Deduplication)
                is_unique, cross_details = await cross_validator.validate(item_data)
                if not is_unique:
                    duplicate_count += 1
                    continue
                
                # Hard Validation
                is_valid_hard, hard_details = await hard_validator.validate(item_data)
                if not is_valid_hard:
                    failed_count += 1
                    # Maybe save as REJECTED content? For now just skip.
                    continue
                    
                # Soft Validation (AI)
                is_valid_soft, soft_details = await soft_validator.validate(item_data)
                if not is_valid_soft:
                    failed_count += 1
                    continue
                
                # 3. Save
                content = ContentItem(
                    source_id=source.id,
                    url=item_data.get("url"),
                    title=item_data.get("title"),
                    content_text=item_data.get("content"),
                    publish_time=item_data.get("published_at"),
                    status="PROCESSED"
                )
                session.add(content)
                await session.flush() # Get ID
                
                # Save validation result
                val_result = ValidationResult(
                    content_id=content.id,
                    hard_result=hard_details,
                    soft_result=soft_details,
                    cross_result=cross_details,
                    overall_score=80 # Placeholder score logic
                )
                session.add(val_result)
                
                new_items_count += 1
            
            job.items_new = new_items_count
            job.items_duplicate = duplicate_count
            job.items_failed = failed_count
            job.status = "COMPLETED"
            job.ended_at = datetime.now(timezone.utc)
            
            await session.commit()
            logger.info(f"Job {job.id} completed. New: {new_items_count}, Dupe: {duplicate_count}, Failed: {failed_count}")
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            job.status = "FAILED"
            job.error_message = str(e)
            job.ended_at = datetime.now(timezone.utc)
            await session.commit()
            
        return job

content_processor = ContentProcessor()
