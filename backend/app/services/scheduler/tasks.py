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
from app.services.metabolism_service import MetabolismService

logger = logging.getLogger(__name__)

from app.services.scheduler.crawl_manager import crawl_manager

async def run_content_crawl():
    """
    Task: Check and crawl all due sources, process and save content.
    """
    logger.info("Task started: Content Crawl")
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(InformationSource).where(InformationSource.is_deleted == False))
            sources = result.scalars().all()
            
            now = datetime.now(timezone.utc)
            
            count = 0
            for source in sources:
                interval = timedelta(seconds=source.check_interval or 3600)
                last_checked = source.last_crawled_at or datetime.min.replace(tzinfo=timezone.utc)
                
                # If never crawled or due for crawl
                if (now - last_checked) >= interval:
                    # Check status constraints
                    if source.status in ["ADJUSTING", "ARCHIVED"]:
                        continue
                        
                    logger.info(f"Scheduling crawl for source: {source.name}")
                    await crawl_manager.add_task(source.id, priority=1)
                    count += 1
            
            logger.info(f"Scheduled {count} sources for crawl")
            
        except Exception as e:
            logger.error(f"Task failed: Content Crawl: {e}")

async def run_source_health_check():
    """
    Task: Check sources in MONITORING state and verify health.
    """
    logger.info("Task started: Source Health Check")
    async with AsyncSessionLocal() as db:
        try:
            from app.services.lifecycle_manager import lifecycle_manager
            
            # Use LifecycleManager to check MONITORING sources
            await lifecycle_manager.check_monitoring_sources(db)
            
            # Optional: Check for sources that haven't been crawled in a long time (stuck?)
            # ...
            
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
            logger.error(f"Task failed: Hotspot Lifecycle: {e}")

async def run_content_metabolism():
    """
    Task: Execute content metabolism process (scoring, aging, archiving).
    """
    logger.info("Task started: Content Metabolism")
    async with AsyncSessionLocal() as db:
        try:
            service = MetabolismService(db)
            stats = await service.process_metabolism()
            logger.info(f"Metabolism complete: {stats}")
        except Exception as e:
            logger.error(f"Task failed: Content Metabolism: {e}")

from app.services.evolution.evolution_engine import evolution_engine

async def run_evolution_cycle():
    """
    Task: Run the full self-evolution cycle (Health -> Strategy -> Structure -> Drift).
    """
    logger.info("Task started: Evolution Cycle")
    try:
        results = await evolution_engine.run_cycle()
        logger.info(f"Evolution Cycle Results: {results}")
    except Exception as e:
        logger.error(f"Task failed: Evolution Cycle: {e}")

async def run_drift_detection():
    """
    Task: Run concept drift detection on all pyramids.
    """
    logger.info("Task started: Drift Detection")
    async with AsyncSessionLocal() as db:
        try:
            # Fetch all active pyramids
            result = await db.execute(select(Pyramid).where(Pyramid.is_deleted == False))
            pyramids = result.scalars().all()
            
            detector = DriftDetector(db)
            count = 0
            for pyramid in pyramids:
                proposals = await detector.detect_drift(pyramid.id)
                count += len(proposals)
                
            logger.info(f"Drift detection complete. Generated {count} proposals across {len(pyramids)} pyramids.")
        except Exception as e:
            logger.error(f"Task failed: Drift Detection: {e}")

async def run_strategy_optimization():
    """
    Task: Optimize crawl strategies based on history.
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
    Task: Discover new topic clusters in unclassified content.
    """
    logger.info("Task started: Cluster Discovery")
    # Placeholder for cluster discovery implementation
    logger.info("Cluster discovery not yet implemented.")

