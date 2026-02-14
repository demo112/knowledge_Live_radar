import logging
from typing import Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.health_report import HealthReportType
from app.models.pyramid import Pyramid
from app.services.evolution.health_detector import HealthDetector
from app.services.evolution.strategy_adapter import StrategyAdapter
from app.services.evolution.restructure_advisor import RestructureAdvisor
from app.services.evolution.drift_detector import DriftDetector
from app.services.evolution.hotspot_manager import HotspotManager

logger = logging.getLogger(__name__)

class EvolutionEngine:
    """
    Orchestrates the self-evolution loop:
    1. Health Detection -> Generate Report
    2. Strategy Adaptation -> Adjust Crawl Frequencies
    3. Hotspot Analysis -> Detect Emerging Topics
    4. Structural Analysis -> Suggest Refactoring (Pyramid)
    5. Drift Detection -> Suggest Concept Updates (Content)
    """
    
    async def run_cycle(self) -> Dict[str, Any]:
        """
        Executes a full evolution cycle.
        Returns a summary of actions taken.
        """
        logger.info("Starting Evolution Cycle")
        results = {
            "health_score": 0.0,
            "strategies_updated": 0,
            "hotspots_updated": False,
            "structure_proposals": 0,
            "drift_proposals": 0,
            "errors": []
        }
        
        async with AsyncSessionLocal() as db:
            try:
                # 1. Health Check
                # This generates a HealthReport record in DB
                detector = HealthDetector(db)
                report = await detector.run_full_detection(report_type=HealthReportType.EVOLUTION_CYCLE)
                results["health_score"] = report.overall_score
                logger.info(f"Health Check Complete. Score: {report.overall_score}")
                
                # 2. Strategy Adaptation
                # Optimizes crawl intervals based on source performance
                adapter = StrategyAdapter(db)
                await adapter.optimize_strategies()
                # StrategyAdapter doesn't return count easily, but we can assume it ran.
                results["strategies_updated"] = 1 
                
                # 3. Hotspot Analysis
                # Updates trends and statuses of hotspots
                hotspot_manager = HotspotManager(db)
                await hotspot_manager.update_hotspot_stats()
                results["hotspots_updated"] = True
                
                # 4. Deep Analysis (Pyramid Structure & Content Drift)
                # We iterate over all active pyramids.
                # In a large system, we might want to prioritize based on health score or rotation.
                
                pyramids_result = await db.execute(select(Pyramid))
                pyramids = pyramids_result.scalars().all()
                
                restructure = RestructureAdvisor(db)
                drift = DriftDetector(db)
                
                total_structure_proposals = 0
                total_drift_proposals = 0
                
                for pyramid in pyramids:
                    try:
                        # Structure Analysis
                        s_proposals = await restructure.analyze_and_propose(pyramid.id)
                        total_structure_proposals += len(s_proposals)
                        
                        # Drift Analysis
                        d_proposals = await drift.detect_drift(pyramid.id)
                        total_drift_proposals += len(d_proposals)
                        
                    except Exception as p_exc:
                        logger.error(f"Error analyzing pyramid {pyramid.id}: {p_exc}")
                        results["errors"].append(f"Pyramid {pyramid.id}: {str(p_exc)}")
                
                results["structure_proposals"] = total_structure_proposals
                results["drift_proposals"] = total_drift_proposals
                
                # Commit any changes made by advisors if they didn't commit themselves
                # (Advisors usually commit, but good to be safe or just close session)
                await db.commit()
                
                logger.info(f"Evolution Cycle Completed: {results}")
                return results
                
            except Exception as e:
                logger.error(f"Evolution Cycle Failed: {e}", exc_info=True)
                await db.rollback()
                results["errors"].append(str(e))
                # We re-raise to ensure the task is marked as failed in scheduler
                raise e

# Singleton instance
evolution_engine = EvolutionEngine()
