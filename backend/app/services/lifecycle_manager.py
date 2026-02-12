from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class LifecycleManager:
    async def update_source_status(self, source: InformationSource, job: CrawlJob, session: AsyncSession):
        """
        Update source status based on job result.
        """
        if job.status == "FAILED" or job.items_failed > 0:
            # Consider partial failure as error for counting? 
            # If job failed completely (status=FAILED), definitely count error.
            # If items_failed > 0 but status=COMPLETED, maybe not a critical error unless ratio is high.
            # Let's stick to job.status == "FAILED" for critical errors.
            pass

        if job.status == "FAILED":
            source.error_count += 1
            source.last_error_message = job.error_message
            
            if source.error_count >= 3:
                source.status = "ERROR"
                logger.warning(f"Source {source.name} disabled due to too many errors.")
        else:
            # Reset error count on success
            if source.error_count > 0:
                source.error_count = 0
                source.last_error_message = None
            
            source.last_crawled_at = datetime.now(timezone.utc)
            if source.status == "ERROR":
                source.status = "ACTIVE"
                logger.info(f"Source {source.name} recovered from ERROR state.")
        
        session.add(source)
        await session.commit()

lifecycle_manager = LifecycleManager()
