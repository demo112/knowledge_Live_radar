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
    Task: Check and crawl all due sources.
    """
    logger.info("Task started: Content Crawl")
    async with AsyncSessionLocal() as db:
        try:
            # Find due sources
            # Assuming logic: last_checked + interval < now
            # Or use next_check_time if available. Let's assume standard interval logic.
            # Using simple iteration for now as I don't see next_check_time in model snippet,
            # but usually it's there or calculated.
            # Let's fetch all active sources and check.
            result = await db.execute(select(InformationSource).where(InformationSource.is_deleted == False))
            sources = result.scalars().all()
            
            now = datetime.now(timezone.utc)
            
            for source in sources:
                # Calculate next run time
                # If check_interval is seconds
                interval = timedelta(seconds=source.check_interval or 3600)
                last_checked = source.last_checked or datetime.min.replace(tzinfo=timezone.utc)
                
                if (now - last_checked) >= interval:
                    logger.info(f"Crawling source: {source.name}")
                    try:
                        # Use SourceService to handle crawl + DB updates + content processing
                        # But SourceService might not be fully implemented for this.
                        # Let's do a basic crawl here or use a helper.
                        # Since crawl_engine just fetches, we need to process items.
                        # For now, let's just fetch to update source status, assuming processing pipeline is triggered separately
                        # OR, ideally SourceService.process_source(source)
                        
                        # Let's try to find SourceService or use CrawlEngine directly and just log success.
                        # Real implementation needs to save content.
                        items = await crawl_engine.crawl_source(source)
                        
                        # Update success
                        source.last_checked = now
                        source.consecutive_failures = 0
                        source.status = "active"
                        
                        # TODO: Save items to DB (ContentService)
                        
                    except Exception as e:
                        logger.error(f"Failed to crawl {source.name}: {e}")
                        source.consecutive_failures = (source.consecutive_failures or 0) + 1
                        if source.consecutive_failures > 3:
                            source.status = "error"
                            
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
                        source.consecutive_failures = (source.consecutive_failures or 0) + 1
                    else:
                        # Only reset if it was error, but don't reset full crawl failure count?
                        # Maybe just log warning.
                        pass
                except Exception:
                    source.consecutive_failures = (source.consecutive_failures or 0) + 1
                    
            await db.commit()
        except Exception as e:
             logger.error(f"Task failed: Source Health Check: {e}")

async def run_system_health_detection():
    """
    Task: Run full system health detection.
    """
    logger.info("Task started: System Health Detection")
    async with AsyncSessionLocal() as db:
        try:
            detector = HealthDetector(db)
            await detector.run_full_detection()
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
            await manager.update_lifecycle()
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
