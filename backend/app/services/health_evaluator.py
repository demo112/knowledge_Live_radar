from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.pyramid import PyramidRepository
from app.models.content import ContentItem, ContentNodeRelation
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
            return {"score": 0, "details": [], "suggestions": []}

        nodes = pyramid.nodes
        total_nodes = len(nodes)
        if total_nodes == 0:
             return {"score": 100, "details": {"depth_score": 100, "coverage_score": 100, "activity_score": 100}, "suggestions": ["Pyramid is empty"]}

        # 1. Depth Balance (Standard Deviation of leaf depths)
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

        # 2. Node Coverage (Empty nodes ratio)
        empty_nodes = sum(1 for n in nodes if not n.description)
        coverage_score = int((1 - empty_nodes / total_nodes) * 100)

        # 3. Update Activity — real calculation based on recent content
        activity_score = await self._calculate_activity_score(pyramid_id, nodes)

        total_score = int(depth_score * 0.4 + coverage_score * 0.4 + activity_score * 0.2)
        
        suggestions = []
        if depth_score < 60:
            suggestions.append("Consider balancing the pyramid depth.")
        if coverage_score < 60:
            suggestions.append("Fill in descriptions for empty nodes.")
        if activity_score < 40:
            suggestions.append("Pyramid has low update activity. Consider adding more sources or checking crawl health.")
        elif activity_score < 70:
            suggestions.append("Pyramid update activity is moderate. Some nodes may need more active sources.")

        return {
            "score": total_score,
            "details": {
                "depth_score": depth_score,
                "coverage_score": coverage_score,
                "activity_score": activity_score
            },
            "suggestions": suggestions
        }

    async def _calculate_activity_score(self, pyramid_id: UUID, nodes: list) -> int:
        """
        Calculate activity score based on recent content updates.
        
        Logic:
        - Count content items linked to this pyramid's nodes in the last 7 days
        - Score = min(100, (recent_content_count / total_nodes) * 50)
        - Also factor in the ratio of nodes that received updates
        """
        if not nodes:
            return 0

        node_ids = [n.id for n in nodes]
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        try:
            # Count recent content linked to any node in this pyramid
            recent_count_result = await self.db.execute(
                select(func.count(ContentNodeRelation.content_id.distinct()))
                .join(ContentItem, ContentItem.id == ContentNodeRelation.content_id)
                .where(
                    ContentNodeRelation.node_id.in_(node_ids),
                    ContentItem.created_at >= seven_days_ago,
                )
            )
            recent_content_count = recent_count_result.scalar() or 0

            # Count how many nodes received at least one update
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

            # Content volume score: how much new content relative to node count
            volume_score = min(100, (recent_content_count / max(total_nodes, 1)) * 50)

            # Coverage score: what fraction of nodes got updates
            node_coverage = (active_node_count / total_nodes) * 100

            # Weighted combination: 60% volume, 40% coverage
            activity_score = int(volume_score * 0.6 + node_coverage * 0.4)
            return max(0, min(100, activity_score))

        except Exception as e:
            logger.error(f"Error calculating activity score for pyramid {pyramid_id}: {e}")
            return 50  # Return neutral score on error instead of hardcoded 100
