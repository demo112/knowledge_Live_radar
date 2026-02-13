import logging
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.config import settings as app_settings

logger = logging.getLogger(__name__)

class StrategyAdapter:
    """
    Adapts crawl strategies (frequency, depth) based on source performance and content freshness.
    """
    
    MIN_INTERVAL = 900 # 15 mins
    MAX_INTERVAL = 86400 # 24 hours
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def optimize_strategies(self):
        """
        Analyze crawl history and adjust check intervals for all active sources.
        """
        logger.info("Starting crawl strategy optimization")
        
        # 1. Fetch active sources
        result = await self.db.execute(
            select(InformationSource).where(InformationSource.is_deleted == False)
        )
        sources = result.scalars().all()
        
        count = 0
        for source in sources:
            changed = await self._optimize_source(source)
            if changed:
                count += 1
            
        if count > 0:
            await self.db.commit()
            logger.info(f"Optimized crawl strategy for {count} sources")
        else:
            logger.info("No strategy adjustments needed")

    async def _optimize_source(self, source: InformationSource) -> bool:
        """
        Analyze a single source and update its config if needed.
        Returns True if changed.
        """
        # 2. Fetch recent jobs (last 5)
        result = await self.db.execute(
            select(CrawlJob)
            .where(CrawlJob.source_id == source.id)
            .where(CrawlJob.status.in_(["COMPLETED", "FAILED"]))
            .order_by(CrawlJob.created_at.desc())
            .limit(5)
        )
        jobs = result.scalars().all()
        
        if not jobs:
            return False

        # 3. Analyze stats
        total_jobs = len(jobs)
        failed_jobs = sum(1 for j in jobs if j.status == "FAILED")
        
        original_interval = source.check_interval
        
        # Rule 1: High failure rate -> Backoff significantly
        if failed_jobs / total_jobs >= app_settings.STRATEGY_FAILURE_THRESHOLD:
            new_interval = min(source.check_interval * app_settings.STRATEGY_BACKOFF_FACTOR, self.MAX_INTERVAL)
            if int(new_interval) != original_interval:
                logger.info(f"Backing off source {source.name} due to errors ({failed_jobs}/{total_jobs}): {original_interval} -> {int(new_interval)}")
                source.check_interval = int(new_interval)
                return True
            return False

        # Check content freshness (only for completed jobs)
        completed_jobs = [j for j in jobs if j.status == "COMPLETED"]
        if not completed_jobs:
            return False
            
        total_fetched = sum(j.items_fetched for j in completed_jobs)
        total_new = sum(j.items_new for j in completed_jobs)
        
        # Rule 2: Low Freshness -> Slow down
        if total_fetched > 0 and total_new == 0:
             new_interval = min(source.check_interval * app_settings.STRATEGY_SLOWDOWN_FACTOR, self.MAX_INTERVAL)
             if int(new_interval) != original_interval:
                logger.info(f"Slowing down source {source.name} due to no new content: {original_interval} -> {int(new_interval)}")
                source.check_interval = int(new_interval)
                return True

        # Rule 3: High Freshness -> Speed up
        if total_fetched > 0 and (total_new / total_fetched) > app_settings.STRATEGY_FRESHNESS_THRESHOLD:
             new_interval = max(source.check_interval * app_settings.STRATEGY_SPEEDUP_FACTOR, self.MIN_INTERVAL)
             if int(new_interval) != original_interval:
                logger.info(f"Speeding up source {source.name} due to high freshness: {original_interval} -> {int(new_interval)}")
                source.check_interval = int(new_interval)
                return True
             
        return False
