import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.source import InformationSource
from app.services.config.configuration_service import ConfigurationService
from app.services.crawl_engine import crawl_engine

logger = logging.getLogger(__name__)

class SourceLifecycleManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_service = ConfigurationService()

    async def verify_source(self, source_id: str) -> bool:
        """
        Verify a newly discovered source by attempting a test crawl.
        If successful, moves state to VERIFYING.
        """
        try:
            source_uuid = uuid.UUID(source_id)
        except ValueError:
            logger.error(f"Invalid source_id: {source_id}")
            return False

        stmt = select(InformationSource).where(InformationSource.id == source_uuid)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()

        if not source:
            logger.error(f"Source {source_id} not found")
            return False

        if source.status != "DISCOVERED":
            logger.warning(f"Source {source_id} is in status {source.status}, expected DISCOVERED")
            return False

        logger.info(f"Verifying source {source_id} ({source.url})...")
        
        try:
            # Execute test crawl (fetch only first few items)
            # Assuming crawl_engine has a method to test or we just use normal crawl with limit
            # For now, we'll try to fetch a small batch. 
            # Ideally crawl_engine should support a 'test' mode or limit.
            # Here we just try to fetch and catch exceptions.
            items = await crawl_engine.crawl_source(source)
            
            if items:
                await self._record_state_change(source, "DISCOVERED", "VERIFYING", "Verification crawl successful")
                source.status = "VERIFYING"
                source.trial_runs = 0
                source.trial_successes = 0
                source.error_count = 0
                await self.db.commit()
                await self.db.refresh(source)
                return True
            else:
                logger.warning(f"Verification failed for {source_id}: No items returned")
                source.error_count += 1
                source.last_error_message = "Verification failed: No items returned"
                await self.db.commit()
                return False

        except Exception as e:
            logger.error(f"Verification failed for {source_id}: {str(e)}")
            source.error_count += 1
            source.last_error_message = f"Verification failed: {str(e)}"
            await self.db.commit()
            return False

    async def on_crawl_success(self, source_id: str):
        """
        Callback for successful crawl job.
        Updates lifecycle state based on success.
        """
        try:
            source_uuid = uuid.UUID(source_id)
        except ValueError:
            logger.error(f"Invalid source_id: {source_id}")
            return

        stmt = select(InformationSource).where(InformationSource.id == source_uuid)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()

        if not source:
            return

        previous_status = source.status
        source.error_count = 0
        source.last_error_message = None
        source.last_crawled_at = datetime.now(timezone.utc)

        if source.status == "VERIFYING":
            source.trial_runs += 1
            source.trial_successes += 1
            
            # Check if we can promote to ACTIVE
            # Logic: If success rate > 80% after 5 runs, or just passed N consecutive runs?
            # Requirement 8.4: After N trial runs with success rate > threshold -> ACTIVE
            # Let's use simple logic: 3 consecutive successes or 5 runs with > 80% success
            if source.trial_runs >= 3 and (source.trial_successes / source.trial_runs) >= 0.8:
                await self._record_state_change(source, "VERIFYING", "ACTIVE", "Trial period passed")
                source.status = "ACTIVE"
        
        elif source.status in ["MONITORING", "ADJUSTING"]:
            source.recovery_count += 1
            # Requirement 9.3: If recovery_count >= threshold -> ACTIVE
            if source.recovery_count >= 3:
                await self._record_state_change(source, source.status, "ACTIVE", "Recovered from errors")
                source.status = "ACTIVE"
                source.recovery_count = 0

        await self.db.commit()
        await self.db.refresh(source)

    async def on_crawl_failure(self, source_id: str, error_message: str):
        """
        Callback for failed crawl job.
        Updates lifecycle state based on failure.
        """
        try:
            source_uuid = uuid.UUID(source_id)
        except ValueError:
            logger.error(f"Invalid source_id: {source_id}")
            return

        stmt = select(InformationSource).where(InformationSource.id == source_uuid)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()

        if not source:
            return

        source.error_count += 1
        source.recovery_count = 0 # Reset recovery on failure
        source.last_error_message = error_message
        
        previous_status = source.status

        # Requirement 8.5, 8.7, 8.8: State transitions based on error count
        if source.status == "ACTIVE":
            if source.error_count >= 3:
                await self._record_state_change(source, "ACTIVE", "MONITORING", f"Consecutive errors: {source.error_count}")
                source.status = "MONITORING"
        
        elif source.status == "MONITORING":
            if source.error_count >= 5:
                await self._record_state_change(source, "MONITORING", "ADJUSTING", f"Consecutive errors: {source.error_count}")
                source.status = "ADJUSTING"
        
        elif source.status == "ADJUSTING":
            if source.error_count >= 10:
                await self._record_state_change(source, "ADJUSTING", "DEAD", f"Consecutive errors: {source.error_count}")
                source.status = "DEAD"

        await self.db.commit()
        await self.db.refresh(source)

    async def _record_state_change(self, source: InformationSource, old_status: str, new_status: str, reason: str):
        """
        Record state change history.
        Currently logs to console/file, can be extended to DB table.
        """
        logger.info(f"Source {source.id} ({source.name}) state changed: {old_status} -> {new_status}. Reason: {reason}")
        
        # Requirement 9.6: Notification (Mock for now)
        if new_status in ["MONITORING", "ADJUSTING", "DEAD"]:
            logger.warning(f"ALERT: Source {source.name} moved to {new_status}. Reason: {reason}")
