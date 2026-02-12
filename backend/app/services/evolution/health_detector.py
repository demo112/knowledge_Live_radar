import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_report import HealthReport, HealthReportType
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource
from app.models.content import ContentItem
from app.models.approval import Approval
from app.models.hotspot import Hotspot
from app.models.crawl_job import CrawlJob

logger = logging.getLogger(__name__)

class HealthDetector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_full_detection(self, report_type: HealthReportType = HealthReportType.SCHEDULED) -> HealthReport:
        logger.info(f"Starting full system health detection (type={report_type})")
        
        try:
            # 1. Evaluate Pyramid Structure
            pyramid_scores, pyramid_issues = await self.evaluate_pyramid_structure()
            
            # 2. Evaluate Source Health
            source_score, source_issues = await self.evaluate_source_health()
            
            # 3. Evaluate Content Coverage
            coverage_score, coverage_issues = await self.evaluate_content_coverage()
            
            # 4. Evaluate Hotspot Distribution
            hotspot_stats, hotspot_issues = await self.evaluate_hotspot_distribution()
            
            # 5. Evaluate Approval Backlog
            backlog_stats, backlog_issues = await self.evaluate_approval_backlog()
            
            # 6. Collect Crawl Stats
            crawl_stats = await self.collect_crawl_stats()
            
            # Calculate Overall Score (Weighted Average)
            # Weights: Pyramid=0.3, Source=0.3, Coverage=0.2, Backlog=0.2
            avg_pyramid_score = sum(pyramid_scores.values()) / len(pyramid_scores) if pyramid_scores else 100.0
            
            # Base overall score calculation
            overall_score = (
                avg_pyramid_score * 0.3 +
                source_score * 0.3 +
                coverage_score * 0.2 +
                (100 - min(backlog_stats.get("backlog_penalty", 0), 100)) * 0.2
            )
            
            all_issues = pyramid_issues + source_issues + coverage_issues + hotspot_issues + backlog_issues
            
            report = HealthReport(
                report_type=report_type,
                overall_score=round(overall_score, 1),
                pyramid_scores=pyramid_scores,
                source_health_score=round(source_score, 1),
                content_coverage_score=round(coverage_score, 1),
                hotspot_distribution=hotspot_stats,
                approval_backlog=backlog_stats,
                crawl_stats=crawl_stats,
                issues=all_issues
            )
            
            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)
            
            logger.info(f"Health detection completed. Overall Score: {report.overall_score}")
            return report
            
        except Exception as e:
            logger.error(f"Error during health detection: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise

    async def evaluate_pyramid_structure(self) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
        scores = {}
        issues = []
        
        result = await self.db.execute(select(Pyramid))
        pyramids = result.scalars().all()
        
        for pyramid in pyramids:
            score = 100.0
            # Check node count
            count_result = await self.db.execute(
                select(func.count(PyramidNode.id)).where(PyramidNode.pyramid_id == pyramid.id)
            )
            node_count = count_result.scalar() or 0
            
            if node_count == 0:
                score -= 50
                issues.append({
                    "type": "empty_pyramid",
                    "severity": "high",
                    "description": f"Pyramid '{pyramid.name}' has no nodes",
                    "entity_id": str(pyramid.id)
                })
            elif node_count < 3:
                score -= 20
                issues.append({
                    "type": "sparse_pyramid",
                    "severity": "medium",
                    "description": f"Pyramid '{pyramid.name}' has very few nodes ({node_count})",
                    "entity_id": str(pyramid.id)
                })
                
            scores[str(pyramid.id)] = max(0.0, score)
            
        return scores, issues

    async def evaluate_source_health(self) -> Tuple[float, List[Dict[str, Any]]]:
        result = await self.db.execute(select(InformationSource))
        sources = result.scalars().all()
        if not sources:
            return 100.0, []
            
        total_score = 0.0
        issues = []
        
        for source in sources:
            source_score = 100.0
            
            # Penalty for consecutive failures
            if source.consecutive_failures > 0:
                penalty = min(source.consecutive_failures * 10, 80)
                source_score -= penalty
                issues.append({
                    "type": "source_failing",
                    "severity": "high" if source.consecutive_failures > 3 else "medium",
                    "description": f"Source '{source.name}' failing ({source.consecutive_failures} times)",
                    "entity_id": str(source.id)
                })
                
            total_score += max(0.0, source_score)
            
        return total_score / len(sources), issues

    async def evaluate_content_coverage(self) -> Tuple[float, List[Dict[str, Any]]]:
        # Check if we have new content in last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        count_result = await self.db.execute(
            select(func.count(ContentItem.id)).where(ContentItem.created_at >= yesterday)
        )
        new_content_count = count_result.scalar() or 0
        
        issues = []
        score = 100.0
        
        if new_content_count == 0:
            score = 50.0
            issues.append({
                "type": "no_new_content",
                "severity": "medium",
                "description": "No new content fetched in last 24 hours",
                "entity_id": None
            })
        elif new_content_count < 10: # Threshold
             score = 80.0
             
        return score, issues

    async def evaluate_hotspot_distribution(self) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
        stats = {}
        issues = []
        
        # Group hotspots by status
        try:
            result = await self.db.execute(
                select(Hotspot.status, func.count(Hotspot.id)).group_by(Hotspot.status)
            )
            results = result.all()
            
            for status, count in results:
                # Handle Enum if necessary by converting to string
                status_key = status.value if hasattr(status, 'value') else str(status)
                stats[status_key] = count
                
        except Exception as e:
            logger.warning(f"Could not evaluate hotspot distribution: {e}")
            stats = {"error": 1}
        
        return stats, issues

    async def evaluate_approval_backlog(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        count_result = await self.db.execute(
            select(func.count(Approval.id)).where(Approval.status == "pending")
        )
        pending_count = count_result.scalar() or 0
        
        stats = {"pending_count": pending_count}
        issues = []
        penalty = 0
        
        if pending_count > 50:
            penalty = 50
            issues.append({
                "type": "high_backlog",
                "severity": "high",
                "description": f"High approval backlog: {pending_count} pending proposals",
                "entity_id": None
            })
        elif pending_count > 20:
            penalty = 20
            issues.append({
                "type": "moderate_backlog",
                "severity": "medium",
                "description": f"Moderate approval backlog: {pending_count} pending proposals",
                "entity_id": None
            })
            
        stats["backlog_penalty"] = penalty
        return stats, issues

    async def collect_crawl_stats(self) -> Dict[str, Any]:
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        try:
            result = await self.db.execute(
                select(CrawlJob).where(CrawlJob.started_at >= yesterday)
            )
            jobs = result.scalars().all()
            
            total_jobs = len(jobs)
            total_items = sum((j.items_new or 0) for j in jobs)
            # Assuming status is a string, e.g., 'failed'
            failed_jobs = sum(1 for j in jobs if str(j.status).lower() == "failed")
            
            return {
                "jobs_last_24h": total_jobs,
                "items_new_last_24h": total_items,
                "failed_jobs_last_24h": failed_jobs
            }
        except Exception as e:
            logger.warning(f"Could not collect crawl stats: {e}")
            return {}
