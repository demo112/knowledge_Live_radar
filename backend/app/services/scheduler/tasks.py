import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.source import InformationSource
from app.models.pyramid import Pyramid
from app.services.crawl_engine import crawl_engine
from app.services.evolution.health_detector import HealthDetector
from app.services.evolution.hotspot_manager import HotspotManager
from app.services.evolution.drift_detector import DriftDetector
from app.services.evolution.strategy_adapter import StrategyAdapter
from app.services.source_service import SourceService

logger = logging.getLogger(__name__)

async def run_content_crawl():
    """
    Task: Check and crawl all due sources, process and save content.
    """
    logger.info("Task started: Content Crawl")
    async with AsyncSessionLocal() as db:
        try:
            from app.services.content_processor import content_processor
            
            result = await db.execute(select(InformationSource).where(InformationSource.is_deleted == False))
            sources = result.scalars().all()
            
            now = datetime.now(timezone.utc)
            
            for source in sources:
                interval = timedelta(seconds=source.check_interval or 3600)
                last_checked = source.last_crawled_at or datetime.min.replace(tzinfo=timezone.utc)
                
                if (now - last_checked) >= interval:
                    logger.info(f"Crawling source: {source.name}")
                    try:
                        # Use ContentProcessor for full pipeline: fetch → validate → AI enhance → save
                        job = await content_processor.process_source(source, db)
                        
                        # Update source metadata
                        source.last_crawled_at = now
                        source.error_count = 0
                        if source.status == "error":
                            source.status = "active"
                        
                        logger.info(f"Source '{source.name}' crawl completed: job {job.id}, status={job.status}")
                        
                    except Exception as e:
                        logger.error(f"Failed to crawl {source.name}: {e}")
                        source.error_count = (source.error_count or 0) + 1
                        if source.error_count > 3:
                            source.status = "error"
                            # Send health alert for failing source
                            from app.services.notification_service import notification_service
                            await notification_service.notify_source_health_alert(
                                source_name=source.name,
                                source_id=str(source.id),
                                error_count=source.error_count,
                            )
                            
                    db.add(source)
                    
            await db.commit()
            
        except Exception as e:
            logger.error(f"Task failed: Content Crawl: {e}")

async def run_source_health_check():
    """
    Task: Verify source accessibility (HEAD request).
    """
    logger.info("Task started: Source Health Check")
    # This might be redundant if crawl runs often.
    # Implementing a lightweight check.
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(InformationSource).where(InformationSource.is_deleted == False))
            sources = result.scalars().all()
            
            for source in sources:
                try:
                    is_valid = await crawl_engine.validate_source(source.type, source.url)
                    if not is_valid:
                        source.error_count = (source.error_count or 0) + 1
                    else:
                        # Only reset if it was error, but don't reset full crawl failure count?
                        # Maybe just log warning.
                        pass
                except Exception:
                    source.error_count = (source.error_count or 0) + 1
                    
            await db.commit()
        except Exception as e:
             logger.error(f"Task failed: Source Health Check: {e}")

async def run_system_health_detection():
    """
    Task: Run full system health detection and send notification.
    """
    logger.info("Task started: System Health Detection")
    async with AsyncSessionLocal() as db:
        try:
            detector = HealthDetector(db)
            report = await detector.run_full_detection()
            
            # Send notification with health results
            from app.services.notification_service import notification_service
            await notification_service.notify_system_health(
                overall_score=report.overall_score,
                issues_count=len(report.issues) if report.issues else 0,
            )
        except Exception as e:
            logger.error(f"Task failed: System Health Detection: {e}")

async def run_hotspot_lifecycle():
    """
    Task: Update hotspot lifecycle states.
    """
    logger.info("Task started: Hotspot Lifecycle Update")
    async with AsyncSessionLocal() as db:
        try:
            manager = HotspotManager(db)
            await manager.update_hotspot_stats()
        except Exception as e:
            logger.error(f"Task failed: Hotspot Lifecycle Update: {e}")

async def run_drift_detection():
    """
    Task: Detect concept drift for all pyramids.
    """
    logger.info("Task started: Concept Drift Detection")
    async with AsyncSessionLocal() as db:
        try:
            detector = DriftDetector(db)
            
            # Fetch all pyramids
            result = await db.execute(select(Pyramid))
            pyramids = result.scalars().all()
            
            for pyramid in pyramids:
                await detector.detect_drift(pyramid.id)
                
        except Exception as e:
             logger.error(f"Task failed: Concept Drift Detection: {e}")

async def run_strategy_optimization():
    """
    Task: Optimize crawl strategies.
    """
    logger.info("Task started: Strategy Optimization")
    async with AsyncSessionLocal() as db:
        try:
            adapter = StrategyAdapter(db)
            await adapter.optimize_strategies()
        except Exception as e:
            logger.error(f"Task failed: Strategy Optimization: {e}")

async def run_cluster_discovery():
    """
    Task: Discover new topic clusters from unlinked content for all pyramids.
    """
    logger.info("Task started: Cluster Discovery")
    async with AsyncSessionLocal() as db:
        try:
            from app.services.evolution_engine import EvolutionEngine
            engine = EvolutionEngine(db)

            result = await db.execute(select(Pyramid))
            pyramids = result.scalars().all()

            for pyramid in pyramids:
                try:
                    await engine.discover_clusters(pyramid.id)
                except Exception as e:
                    logger.error(f"Cluster discovery failed for pyramid {pyramid.id}: {e}")

        except Exception as e:
            logger.error(f"Task failed: Cluster Discovery: {e}")
