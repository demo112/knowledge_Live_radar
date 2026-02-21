from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.knowledge import KnowledgeNode, KnowledgeCluster, KnowledgeNodeRelation, ClusterNodeMembership

class KnowledgeNodeRepository(BaseRepository[KnowledgeNode]):
    def __init__(self, db):
        super().__init__(KnowledgeNode, db)
    
    async def get_with_relations(self, id: UUID) -> Optional[KnowledgeNode]:
        query = select(KnowledgeNode).options(
            selectinload(KnowledgeNode.outgoing_relations),
            selectinload(KnowledgeNode.incoming_relations)
        ).where(KnowledgeNode.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[KnowledgeNode]:
        query = select(KnowledgeNode).where(
            KnowledgeNode.name == name,
            KnowledgeNode.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class KnowledgeClusterRepository(BaseRepository[KnowledgeCluster]):
    def __init__(self, db):
        super().__init__(KnowledgeCluster, db)
    
    async def get_with_members(self, id: UUID) -> Optional[KnowledgeCluster]:
        query = select(KnowledgeCluster).options(
            selectinload(KnowledgeCluster.node_memberships).selectinload(ClusterNodeMembership.node)
        ).where(KnowledgeCluster.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class KnowledgeRelationRepository(BaseRepository[KnowledgeNodeRelation]):
    def __init__(self, db):
        super().__init__(KnowledgeNodeRelation, db)
    
    async def get_relations(self, node_id: UUID) -> List[KnowledgeNodeRelation]:
        query = select(KnowledgeNodeRelation).where(
            (KnowledgeNodeRelation.source_node_id == node_id) | 
            (KnowledgeNodeRelation.target_node_id == node_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_relations_with_nodes(self, node_ids: List[UUID], relation_type: Optional[str] = None) -> List[KnowledgeNodeRelation]:
        if not node_ids:
            return []
            
        query = select(KnowledgeNodeRelation).options(
            selectinload(KnowledgeNodeRelation.source_node),
            selectinload(KnowledgeNodeRelation.target_node)
        ).where(
            (KnowledgeNodeRelation.source_node_id.in_(node_ids)) | 
            (KnowledgeNodeRelation.target_node_id.in_(node_ids))
        )
        
        if relation_type:
            query = query.where(KnowledgeNodeRelation.relation_type == relation_type)
            
        result = await self.db.execute(query)
        return result.scalars().all()
