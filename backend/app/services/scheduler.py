from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.source import InformationSource
from app.services.content_processor import content_processor
from app.services.lifecycle_manager import lifecycle_manager
from datetime import datetime, timezone, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class CrawlScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # Add job to run every 1 minute
        self.scheduler.add_job(self.check_sources, 'interval', minutes=1)
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Crawl Scheduler started")

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Crawl Scheduler stopped")

    async def check_sources(self):
        logger.info("Checking for sources to crawl...")
        async with AsyncSessionLocal() as session:
            try:
                # Fetch all ACTIVE sources
                result = await session.execute(select(InformationSource).where(InformationSource.status == "ACTIVE"))
                sources = result.scalars().all()
                
                now = datetime.now(timezone.utc)
                
                for source in sources:
                    should_crawl = False
                    if not source.last_crawled_at:
                        should_crawl = True
                    else:
                        # Ensure last_crawled_at is timezone aware or handle naive
                        last_crawled = source.last_crawled_at
                        if last_crawled.tzinfo is None:
                             last_crawled = last_crawled.replace(tzinfo=timezone.utc)
                        
                        next_crawl = last_crawled + timedelta(seconds=source.check_interval)
                        if now >= next_crawl:
                            should_crawl = True
                    
                    if should_crawl:
                        logger.info(f"Triggering crawl for {source.name}")
                        try:
                            # Await processing to avoid overwhelming system/DB with concurrent jobs in this loop
                            job = await content_processor.process_source(source, session)
                            await lifecycle_manager.update_source_status(source, job, session)
                        except Exception as e:
                            logger.error(f"Error processing source {source.name}: {e}")
                            
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

crawl_scheduler = CrawlScheduler()
