from typing import List, Any
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pyramid import NodeRelationRepository, PyramidNodeRepository
from app.schemas.pyramid import NodeLinkRequest, NodeRelationCreate

class NodeService:
    def __init__(self, db: AsyncSession):
        self.node_repo = PyramidNodeRepository(db)
        self.relation_repo = NodeRelationRepository(db)
        self.db = db

    async def link_nodes(self, source_id: UUID, schema: NodeLinkRequest) -> Any:
        # Verify source and target exist
        source = await self.node_repo.get(source_id)
        target = await self.node_repo.get(schema.target_node_id)
        
        if not source or source.is_deleted:
            raise HTTPException(status_code=404, detail="Source node not found")
        if not target or target.is_deleted:
            raise HTTPException(status_code=404, detail="Target node not found")
            
        # Create relation
        relation_data = NodeRelationCreate(
            target_node_id=schema.target_node_id,
            relation_type=schema.relation_type
        )
        data = relation_data.model_dump()
        data["source_node_id"] = source_id
        
        return await self.relation_repo.create(data)

    async def get_node_relations(self, node_id: UUID) -> List[Any]:
        return await self.relation_repo.get_relations(node_id)
