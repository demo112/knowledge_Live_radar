from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crawl_engine import crawl_engine
from app.services.validator import HardValidator, SoftValidator, CrossValidator
from app.core.ai.facade import ai_facade
from app.services.evolution_engine import EvolutionEngine
from app.services.source_lifecycle_manager import SourceLifecycleManager
from app.models.source import InformationSource
from app.models.content import ContentItem, ValidationResult
from app.models.crawl_job import CrawlJob
from app.services.auto_discovery import auto_discovery
from app.services.fetchers.request_utils import RateLimitException
from typing import List
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ContentProcessor:
    async def process_source(self, source: InformationSource, session: AsyncSession, job: CrawlJob = None) -> CrawlJob:
        if not job:
            job = CrawlJob(
                source_id=source.id, 
                status="RUNNING",
                started_at=datetime.now(timezone.utc)
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
        else:
            job = await session.merge(job)
            job.status = "RUNNING"
            job.started_at = datetime.now(timezone.utc)
            await session.commit()
        
        lifecycle_manager = SourceLifecycleManager(session)
        
        try:
            items = await crawl_engine.crawl_source(source)
            job.items_fetched = len(items)
            
            hard_validator = HardValidator(db=session)
            soft_validator = SoftValidator()
            cross_validator = CrossValidator(session)
            evolution_engine = EvolutionEngine(session)
            
            new_items_count = 0
            failed_count = 0
            duplicate_count = 0
            classified_items_count = 0
            
            for item_data in items:
                is_unique, cross_details = await cross_validator.validate(item_data)
                if not is_unique:
                    duplicate_count += 1
                    continue
                
                is_valid_hard, hard_details = await hard_validator.validate(item_data)
                if not is_valid_hard:
                    failed_count += 1
                    continue
                    
                is_valid_soft, soft_details = await soft_validator.validate(item_data)
                if not is_valid_soft:
                    failed_count += 1
                    continue
                
                title = item_data.get("title", "")
                text = item_data.get("content", "")[:3000]
                
                ai_summary_data = await ai_facade.generate_summary(title, text)
                summary = ai_summary_data.get("summary", "")
                ai_tags = await ai_facade.generate_tags(title, text)
                ai_concepts = await ai_facade.extract_concepts(title, text)
                
                content = ContentItem(
                    source_id=source.id,
                    url=item_data.get("url"),
                    title=title,
                    content_text=item_data.get("content"),
                    publish_time=item_data.get("published_at"),
                    status="PROCESSED",
                    summary=summary,
                    tags=ai_tags,
                    concepts=ai_concepts,
                    ai_processed=bool(summary)
                )
                session.add(content)
                await session.flush()
                
                val_result = ValidationResult(
                    content_id=content.id,
                    hard_result=hard_details,
                    soft_result=soft_details,
                    cross_result=cross_details,
                    overall_score=soft_details.get("score", 80)
                )
                session.add(val_result)
                
                await auto_discovery.process_content_links(content.content_text, session)
                
                try:
                    linked_count = await evolution_engine.auto_classify_content(content)
                    if linked_count > 0:
                        classified_items_count += 1
                except Exception as e:
                    logger.error(f"Auto-classification failed for content {content.id}: {e}")

                new_items_count += 1
            
            job.items_new = new_items_count
            job.items_duplicate = duplicate_count
            job.items_failed = failed_count
            job.items_classified = classified_items_count
            job.status = "COMPLETED"
            job.ended_at = datetime.now(timezone.utc)
            
            await lifecycle_manager.on_crawl_success(str(source.id))
            
            await session.commit()
            logger.info(f"Job {job.id} completed. New: {new_items_count}, Dupe: {duplicate_count}, Failed: {failed_count}, Classified: {classified_items_count}")
            
        except RateLimitException as e:
            logger.warning(f"Job {job.id} rate limited: {e}")
            job.status = "RATE_LIMITED"
            job.error_message = str(e)
            job.ended_at = datetime.now(timezone.utc)
            
            await lifecycle_manager.on_rate_limit(str(source.id))
            
            await session.commit()

        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            job.status = "FAILED"
            job.error_message = str(e)
            job.ended_at = datetime.now(timezone.utc)
            
            await lifecycle_manager.on_crawl_failure(str(source.id), str(e))
            
            await session.commit()
            
        return job

content_processor = ContentProcessor()
