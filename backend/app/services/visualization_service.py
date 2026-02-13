from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pyramid import PyramidRepository

class VisualizationService:
    def __init__(self, db: AsyncSession):
        self.pyramid_repo = PyramidRepository(db)

    async def get_react_flow_data(self, pyramid_id: UUID) -> dict:
        pyramid = await self.pyramid_repo.get_with_nodes(pyramid_id)
        if not pyramid:
            return {"nodes": [], "edges": []}
            
        rf_nodes = []
        rf_edges = []
        
        # Simple tree layout calculation
        level_map = {}
        for node in pyramid.nodes:
            level_map.setdefault(node.level, []).append(node)
            
        # Calculate X positions
        for level, nodes in level_map.items():
            for idx, node in enumerate(nodes):
                rf_nodes.append({
                    "id": str(node.id),
                    "type": "default", 
                    "position": {"x": idx * 250, "y": level * 100},
                    "data": {
                        "label": node.name,
                        "health": node.health_score,
                        "status": node.status
                    }
                })
                
                if node.parent_id:
                    rf_edges.append({
                        "id": f"e{node.parent_id}-{node.id}",
                        "source": str(node.parent_id),
                        "target": str(node.id),
                        "type": "smoothstep"
                    })
                    
        return {"nodes": rf_nodes, "edges": rf_edges}
