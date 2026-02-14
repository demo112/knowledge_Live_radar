from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.models.strategy_adjustment import StrategyAdjustment
from app.models.approval import Approval
from app.services.crawl_engine import crawl_engine
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SourceStatus:
    DISCOVERED = "DISCOVERED"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    MONITORING = "MONITORING"
    ADJUSTING = "ADJUSTING"
    ARCHIVED = "ARCHIVED"
    ERROR = "ERROR" # Deprecated

class LifecycleManager:
    async def update_source_status(self, source: InformationSource, job: CrawlJob, session: AsyncSession):
        """
        Update source status based on job result.
        """
        if job.status == "FAILED":
            source.error_count += 1
            source.last_error_message = job.error_message
            
            if source.status == SourceStatus.ACTIVE and source.error_count >= 3:
                source.status = SourceStatus.MONITORING
                logger.warning(f"Source {source.name} moved to MONITORING due to 3 consecutive errors.")
                
            elif source.status == SourceStatus.MONITORING and source.error_count >= 10:
                source.status = SourceStatus.ADJUSTING
                logger.warning(f"Source {source.name} moved to ADJUSTING due to 10 consecutive errors.")
                await self._create_adjustment_proposal(source, session)
                
        elif job.status == "COMPLETED":
            # Reset error count on success
            if source.error_count > 0:
                source.error_count = 0
                source.last_error_message = None
            
            source.last_crawled_at = datetime.now(timezone.utc)
            
            # Auto-recover
            if source.status in [SourceStatus.MONITORING, SourceStatus.ADJUSTING, SourceStatus.ERROR]:
                source.status = SourceStatus.ACTIVE
                logger.info(f"Source {source.name} recovered to ACTIVE state.")
        
        session.add(source)
        await session.commit()

    async def _create_adjustment_proposal(self, source: InformationSource, session: AsyncSession):
        """
        Create a strategy adjustment proposal for failing source.
        """
        # Check if there is already a pending proposal for this source
        # This prevents flooding approvals
        stmt = select(Approval).where(
            Approval.target_id == source.id,
            Approval.type == "strategy_adjustment",
            Approval.status == "pending"
        )
        result = await session.execute(stmt)
        if result.scalars().first():
            logger.info(f"Pending strategy adjustment proposal already exists for source {source.name}")
            return

        reason = f"Source failed {source.error_count} times consecutively. Last error: {source.last_error_message}"
        
        adjustment = StrategyAdjustment(
            source_id=source.id,
            adjustment_type="manual_intervention",
            reason=reason,
            requires_approval=True
        )
        session.add(adjustment)
        await session.flush() # Get ID for adjustment

        proposal = Approval(
            type="strategy_adjustment",
            target_id=source.id,
            status="pending",
            data={
                "adjustment_id": str(adjustment.id),
                "source_name": source.name,
                "current_status": source.status,
                "error_count": source.error_count
            },
            generated_by="system",
            reason=reason
        )
        session.add(proposal)
        await session.flush()
        
        # Link adjustment to proposal
        adjustment.proposal_id = str(proposal.id)
        
        logger.info(f"Created strategy adjustment proposal for source {source.name}")

    async def check_monitoring_sources(self, session: AsyncSession):
        """
        Periodic task: check sources in MONITORING state.
        Active probing for sources that are failing.
        """
        stmt = select(InformationSource).where(InformationSource.status == SourceStatus.MONITORING)
        result = await session.execute(stmt)
        sources = result.scalars().all()
        
        logger.info(f"Checking {len(sources)} sources in MONITORING state")
        
        for source in sources:
            try:
                # Active probe using validation logic (HEAD request or light fetch)
                is_reachable = await crawl_engine.validate_source(source.type, source.url)
                
                if is_reachable:
                    logger.info(f"Source {source.name} is reachable during monitoring check.")
                    # We don't automatically move to ACTIVE here, 
                    # we let the next scheduled crawl do that to ensure full functionality.
                    # But we could reset error count partially? 
                    # For now, just log.
                else:
                    source.error_count += 1
                    logger.warning(f"Source {source.name} unreachable during monitoring check. Error count: {source.error_count}")
                    
                    if source.error_count >= 10:
                        source.status = SourceStatus.ADJUSTING
                        logger.warning(f"Source {source.name} moved to ADJUSTING due to monitoring failure.")
                        await self._create_adjustment_proposal(source, session)
            
                session.add(source)
            except Exception as e:
                logger.error(f"Error checking source {source.name}: {e}")
        
        await session.commit()



lifecycle_manager = LifecycleManager()
