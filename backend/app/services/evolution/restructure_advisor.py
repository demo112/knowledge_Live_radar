import uuid
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pyramid import PyramidNode
from app.models.approval import Approval

logger = logging.getLogger(__name__)

class RestructureAdvisor:
    """
    Analyzes pyramid structure and suggests refactoring actions.
    """
    
    # Thresholds
    MAX_CHILDREN = 10
    MAX_DEPTH = 5
    MIN_CHILDREN = 2 
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_and_propose(self, pyramid_id: uuid.UUID) -> List[Approval]:
        """
        Analyze the pyramid structure and generate restructuring proposals.
        """
        logger.info(f"Starting structure analysis for pyramid {pyramid_id}")
        
        proposals = []
        
        # 1. Fetch all nodes for the pyramid
        nodes = await self._fetch_nodes(pyramid_id)
        if not nodes:
            logger.warning(f"No nodes found for pyramid {pyramid_id}")
            return []
            
        # 2. Build tree structure in memory for analysis
        node_map = {n.id: n for n in nodes}
        children_map: Dict[uuid.UUID, List[PyramidNode]] = {n.id: [] for n in nodes}
        
        # Root nodes (parent_id is None) are handled implicitly as they won't appear in children lists of others
        for n in nodes:
            if n.parent_id and n.parent_id in children_map:
                children_map[n.parent_id].append(n)
                
        # 3. Analyze for issues
        
        # Check for Overloaded Nodes (Too many children)
        for node in nodes:
            children_count = len(children_map[node.id])
            if children_count > self.MAX_CHILDREN:
                proposals.append(self._create_split_proposal(node, children_count))
                
        # Check for Deep Hierarchy
        for node in nodes:
            if node.level > self.MAX_DEPTH:
                proposals.append(self._create_flatten_proposal(node))

        # Check for Sparse Nodes (Too few children, not leaf)
        # We only check nodes that HAVE children but very few. 
        # Leaf nodes (0 children) are normal.
        for node in nodes:
            children_count = len(children_map[node.id])
            if 0 < children_count < self.MIN_CHILDREN:
                 proposals.append(self._create_merge_proposal(node, children_count))

        # 4. Save proposals
        # First, check if similar pending proposals already exist to avoid duplicates
        existing_proposals = await self._fetch_pending_structure_proposals(pyramid_id)
        existing_keys = set((p.type, p.target_id) for p in existing_proposals)
        
        saved_proposals = []
        for p in proposals:
            if (p.type, p.target_id) not in existing_keys:
                self.db.add(p)
                saved_proposals.append(p)
            
        if saved_proposals:
            await self.db.commit()
            for p in saved_proposals:
                await self.db.refresh(p)
            logger.info(f"Generated {len(saved_proposals)} restructuring proposals")
        else:
            logger.info("No new restructuring proposals generated")
            
        return saved_proposals

    async def _fetch_nodes(self, pyramid_id: uuid.UUID) -> List[PyramidNode]:
        result = await self.db.execute(
            select(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .where(PyramidNode.is_deleted == False)
        )
        return result.scalars().all()

    async def _fetch_pending_structure_proposals(self, pyramid_id: uuid.UUID) -> List[Approval]:
        # Ideally we filter by pyramid_id in JSON data, but for now we'll fetch all pending structure proposals
        # and filter in memory or assume the number isn't huge.
        # A better way is to check target_id which maps to node_id, and check that node's pyramid_id.
        # But for simplicity/speed, let's just fetch pending proposals of structure types.
        
        types = ["split_node", "move_node", "merge_node"]
        result = await self.db.execute(
            select(Approval)
            .where(Approval.status == "pending")
            .where(Approval.type.in_(types))
        )
        all_pending = result.scalars().all()
        
        # Filter strictly for this pyramid if needed. 
        # Since target_id is the node_id, we can verify if the node belongs to this pyramid.
        # But we already fetched nodes.
        
        # Optimization: We know the nodes belonging to this pyramid.
        # So we can just check if target_id is in our list of node IDs.
        node_ids = (await self.db.execute(
            select(PyramidNode.id)
            .where(PyramidNode.pyramid_id == pyramid_id)
        )).scalars().all()
        node_id_set = set(node_ids)
        
        return [p for p in all_pending if p.target_id in node_id_set]

    def _create_split_proposal(self, node: PyramidNode, count: int) -> Approval:
        return Approval(
            type="split_node",
            status="pending",
            target_id=node.id,
            generated_by="ai",
            confidence_score=0.8,
            reason=f"Node '{node.name}' has too many children ({count} > {self.MAX_CHILDREN}). Suggest splitting into sub-categories.",
            data={
                "node_id": str(node.id),
                "node_name": node.name,
                "pyramid_id": str(node.pyramid_id),
                "current_children_count": count,
                "suggested_action": "group_children_by_topic"
            }
        )

    def _create_flatten_proposal(self, node: PyramidNode) -> Approval:
        return Approval(
            type="move_node",
            status="pending",
            target_id=node.id,
            generated_by="ai",
            confidence_score=0.7,
            reason=f"Node '{node.name}' is too deep (level {node.level} > {self.MAX_DEPTH}). Suggest moving up.",
            data={
                "node_id": str(node.id),
                "node_name": node.name,
                "pyramid_id": str(node.pyramid_id),
                "current_level": node.level,
                "suggested_parent_level": node.level - 2
            }
        )
        
    def _create_merge_proposal(self, node: PyramidNode, count: int) -> Approval:
        return Approval(
            type="merge_node",
            status="pending",
            target_id=node.id,
            generated_by="ai",
            confidence_score=0.6,
            reason=f"Node '{node.name}' has too few children ({count} < {self.MIN_CHILDREN}). Suggest merging with siblings.",
            data={
                "node_id": str(node.id),
                "node_name": node.name,
                "pyramid_id": str(node.pyramid_id),
                "current_children_count": count
            }
        )
