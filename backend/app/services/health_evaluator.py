from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pyramid import PyramidRepository
import math

class HealthEvaluator:
    def __init__(self, db: AsyncSession):
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
            depth_score = max(0, 100 - int(std_dev * 20)) # Penalize deviation
        else:
            depth_score = 100

        # 2. Node Coverage (Empty nodes ratio)
        # Assuming 'description' indicates coverage for now
        empty_nodes = sum(1 for n in nodes if not n.description)
        coverage_score = int((1 - empty_nodes / total_nodes) * 100)

        # 3. Update Activity (Recent updates)
        activity_score = 100 # Placeholder

        total_score = int(depth_score * 0.4 + coverage_score * 0.4 + activity_score * 0.2)
        
        suggestions = []
        if depth_score < 60:
            suggestions.append("Consider balancing the pyramid depth.")
        if coverage_score < 60:
            suggestions.append("Fill in descriptions for empty nodes.")

        return {
            "score": total_score,
            "details": {
                "depth_score": depth_score,
                "coverage_score": coverage_score,
                "activity_score": activity_score
            },
            "suggestions": suggestions
        }
