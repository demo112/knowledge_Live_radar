import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.approval import Approval
from app.models.pyramid import PyramidNode

logger = logging.getLogger(__name__)

class ImpactAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_impact(self, approval: Approval) -> Dict[str, Any]:
        """
        Analyzes the impact of an approval request.
        Returns a dictionary containing risk level, affected nodes, and description.
        """
        impact = {
            "risk_level": "low",
            "affected_nodes_count": 0,
            "affected_nodes": [],
            "description": ""
        }
        
        try:
            target_id = approval.target_id
            
            if approval.type == "create_node":
                impact["description"] = "Creating a new node has low impact."
                impact["risk_level"] = "low"
                
            elif approval.type == "update_node" and target_id:
                node = await self._get_node(target_id)
                if node:
                    impact["affected_nodes"].append({"id": str(node.id), "title": node.name, "type": "target"})
                    impact["affected_nodes_count"] = 1
                    impact["description"] = f"Updating node '{node.name}'."
                    impact["risk_level"] = "medium"
                else:
                    impact["description"] = "Target node not found."

            elif approval.type == "delete_node" and target_id:
                node = await self._get_node(target_id)
                if node:
                    impact["affected_nodes"].append({"id": str(node.id), "title": node.name, "type": "target"})
                    
                    # Find children
                    children = await self._get_children(target_id)
                    impact["affected_nodes_count"] = 1 + len(children)
                    for child in children:
                        impact["affected_nodes"].append({"id": str(child.id), "title": child.name, "type": "child"})
                    
                    impact["description"] = f"Deleting node '{node.name}' will affect {len(children)} children."
                    impact["risk_level"] = "high" if len(children) > 0 else "medium"
                else:
                    impact["description"] = "Target node not found."
            
            # Save the analysis result to the approval object (in memory, caller should commit)
            approval.impact_analysis = impact
            return impact
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}")
            return {"error": str(e)}

    async def _get_node(self, node_id) -> Optional[PyramidNode]:
        result = await self.db.execute(select(PyramidNode).where(PyramidNode.id == node_id))
        return result.scalars().first()

    async def _get_children(self, parent_id) -> List[PyramidNode]:
        result = await self.db.execute(select(PyramidNode).where(PyramidNode.parent_id == parent_id))
        return result.scalars().all()
