from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.models.strategy_adjustment import StrategyAdjustment
from app.models.approval import Approval
from app.services.crawl_engine import crawl_engine
from app.core.ai.facade import ai_facade
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
    ERROR = "ERROR"

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
            if source.error_count > 0:
                source.error_count = 0
                source.last_error_message = None
            
            source.last_crawled_at = datetime.now(timezone.utc)
            
            if source.status in [SourceStatus.MONITORING, SourceStatus.ADJUSTING, SourceStatus.ERROR]:
                source.status = SourceStatus.ACTIVE
                logger.info(f"Source {source.name} recovered to ACTIVE state.")
        
        session.add(source)
        await session.commit()

    async def _create_adjustment_proposal(self, source: InformationSource, session: AsyncSession):
        """
        Create a strategy adjustment proposal for failing source.
        使用 AI 分析生成失败原因和建议。
        """
        stmt = select(Approval).where(
            Approval.target_id == source.id,
            Approval.type == "strategy_adjustment",
            Approval.status == "pending"
        )
        result = await session.execute(stmt)
        if result.scalars().first():
            logger.info(f"Pending strategy adjustment proposal already exists for source {source.name}")
            return

        ai_analysis = await self._get_ai_analysis(source)
        
        adjustment = StrategyAdjustment(
            source_id=source.id,
            adjustment_type="manual_intervention",
            reason=ai_analysis.get("summary", f"信息源连续失败 {source.error_count} 次"),
            requires_approval=True
        )
        session.add(adjustment)
        await session.flush()

        proposal = Approval(
            type="strategy_adjustment",
            target_id=source.id,
            status="pending",
            data={
                "adjustment_id": str(adjustment.id),
                "source_name": source.name,
                "current_status": source.status,
                "error_count": source.error_count,
                "ai_analysis": ai_analysis,
            },
            generated_by="ai",
            reason=ai_analysis.get("summary", f"信息源连续失败 {source.error_count} 次")
        )
        session.add(proposal)
        await session.flush()
        
        adjustment.proposal_id = str(proposal.id)
        
        logger.info(f"Created strategy adjustment proposal for source {source.name}")

    async def _get_ai_analysis(self, source: InformationSource) -> dict:
        """
        调用 AI 分析信息源健康状态，生成失败原因和建议。
        """
        try:
            result = await ai_facade.analyze_source_health(str(source.id))
            
            if result.get("error"):
                logger.warning(f"AI 分析失败: {result['error']}, 使用默认描述")
                return self._get_default_analysis(source)
            
            suggestions = result.get("suggestions", [])
            analysis = result.get("analysis", {})
            
            summary = analysis.get("summary", "")
            if not summary and suggestions:
                summary = suggestions[0].get("reason", f"信息源连续失败 {source.error_count} 次")
            
            return {
                "summary": summary,
                "suggestions": suggestions,
                "analysis": analysis,
                "suggestion_ids": result.get("suggestion_ids", []),
            }
            
        except Exception as e:
            logger.error(f"AI 分析异常: {e}")
            return self._get_default_analysis(source)

    def _get_default_analysis(self, source: InformationSource) -> dict:
        """
        生成默认的分析结果（当 AI 分析失败时使用）。
        """
        return {
            "summary": f"信息源「{source.name}」连续失败 {source.error_count} 次，最后错误: {source.last_error_message}",
            "suggestions": [
                {
                    "action_type": "manual_intervention",
                    "target_id": str(source.id),
                    "target_name": source.name,
                    "reason": "连续失败次数过多，需要人工检查",
                    "params": {},
                    "confidence": 0.5,
                    "priority": "high"
                }
            ],
            "analysis": {
                "error_pattern": "consecutive_failures",
                "error_count": source.error_count,
                "last_error": source.last_error_message,
            },
            "suggestion_ids": [],
        }

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
                is_reachable = await crawl_engine.validate_source(source.type, source.url)
                
                if is_reachable:
                    logger.info(f"Source {source.name} is reachable during monitoring check.")
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
