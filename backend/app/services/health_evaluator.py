from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.pyramid import PyramidRepository
from app.models.content import ContentItem, ContentNodeRelation
from app.core.ai.facade import ai_facade
import math
import logging

logger = logging.getLogger(__name__)

class HealthEvaluator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pyramid_repo = PyramidRepository(db)

    async def evaluate_pyramid(self, pyramid_id: UUID) -> dict:
        pyramid = await self.pyramid_repo.get_with_nodes(pyramid_id)
        if not pyramid:
            return {"score": 0, "details": {}, "suggestions": [], "analysis": {}}

        nodes = pyramid.nodes
        total_nodes = len(nodes)
        if total_nodes == 0:
            return {
                "score": 100,
                "details": {"depth_score": 100, "coverage_score": 100, "activity_score": 100},
                "suggestions": [],
                "analysis": {"message": "金字塔为空"}
            }

        depth_score = self._calculate_depth_score(nodes)
        coverage_score = self._calculate_coverage_score(nodes, total_nodes)
        activity_score = await self._calculate_activity_score(pyramid_id, nodes)

        total_score = int(depth_score * 0.4 + coverage_score * 0.4 + activity_score * 0.2)

        return {
            "score": total_score,
            "details": {
                "depth_score": depth_score,
                "coverage_score": coverage_score,
                "activity_score": activity_score
            },
            "suggestions": [],
            "analysis": {}
        }

    async def analyze_with_ai(self, pyramid_id: UUID) -> dict:
        base_result = await self.evaluate_pyramid(pyramid_id)
        if base_result["score"] == 0:
            return base_result

        ai_result = await self._get_ai_suggestions(pyramid_id)
        base_result["suggestions"] = ai_result.get("suggestions", [])
        base_result["analysis"] = ai_result.get("analysis", {})
        return base_result

    def _calculate_depth_score(self, nodes: list) -> int:
        parent_ids = set(n.parent_id for n in nodes if n.parent_id)
        leaves = [n for n in nodes if n.id not in parent_ids]

        depths = [n.level for n in leaves]
        if depths:
            avg_depth = sum(depths) / len(depths)
            variance = sum((d - avg_depth) ** 2 for d in depths) / len(depths)
            std_dev = math.sqrt(variance)
            depth_score = max(0, 100 - int(std_dev * 20))
        else:
            depth_score = 100

        return depth_score

    def _calculate_coverage_score(self, nodes: list, total_nodes: int) -> int:
        empty_nodes = sum(1 for n in nodes if not n.description)
        coverage_score = int((1 - empty_nodes / total_nodes) * 100)
        return coverage_score

    async def _get_ai_suggestions(self, pyramid_id: UUID) -> dict:
        try:
            ai_result = await ai_facade.analyze_pyramid_health(str(pyramid_id), self.db)
            return ai_result
        except Exception as e:
            logger.error(f"获取 AI 建议失败，金字塔 {pyramid_id}: {e}")
            return {"suggestions": [], "analysis": {"error": str(e)}}

    async def _calculate_activity_score(self, pyramid_id: UUID, nodes: list) -> int:
        if not nodes:
            return 0

        node_ids = [n.id for n in nodes]
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        try:
            recent_count_result = await self.db.execute(
                select(func.count(ContentNodeRelation.content_id.distinct()))
                .join(ContentItem, ContentItem.id == ContentNodeRelation.content_id)
                .where(
                    ContentNodeRelation.node_id.in_(node_ids),
                    ContentItem.created_at >= seven_days_ago,
                )
            )
            recent_content_count = recent_count_result.scalar() or 0

            active_nodes_result = await self.db.execute(
                select(func.count(ContentNodeRelation.node_id.distinct()))
                .join(ContentItem, ContentItem.id == ContentNodeRelation.content_id)
                .where(
                    ContentNodeRelation.node_id.in_(node_ids),
                    ContentItem.created_at >= seven_days_ago,
                )
            )
            active_node_count = active_nodes_result.scalar() or 0

            total_nodes = len(nodes)

            volume_score = min(100, (recent_content_count / max(total_nodes, 1)) * 50)

            node_coverage = (active_node_count / total_nodes) * 100

            activity_score = int(volume_score * 0.6 + node_coverage * 0.4)
            return max(0, min(100, activity_score))

        except Exception as e:
            logger.error(f"计算活跃度分数失败，金字塔 {pyramid_id}: {e}")
            return 50
