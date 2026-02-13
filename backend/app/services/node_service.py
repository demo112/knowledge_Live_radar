from typing import List, Any, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.repositories.pyramid import NodeRelationRepository, PyramidNodeRepository
from app.schemas.pyramid import NodeLinkRequest, NodeRelationCreate
from app.models.content import ContentNodeRelation
from app.models.pyramid import PyramidNode

class NodeService:
    def __init__(self, db: AsyncSession):
        self.node_repo = PyramidNodeRepository(db)
        self.relation_repo = NodeRelationRepository(db)
        self.db = db

    async def link_content(self, node_id: UUID, content_id: UUID, source: str = "manual", confidence: float = 1.0) -> Any:
        """
        Link a content item to a node and update node stats.
        """
        # Check node exists
        node = await self.node_repo.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        # Check if relation already exists
        stmt = select(ContentNodeRelation).where(
            ContentNodeRelation.node_id == node_id,
            ContentNodeRelation.content_id == content_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing

        try:
            # Create relation
            relation = ContentNodeRelation(
                node_id=node_id,
                content_id=content_id,
                source=source,
                confidence=confidence
            )
            self.db.add(relation)
            
            # Update node stats
            await self.db.execute(
                update(PyramidNode)
                .where(PyramidNode.id == node_id)
                .values(
                    content_count=PyramidNode.content_count + 1,
                    last_content_at=func.now()
                )
            )
            
            await self.db.commit()
            await self.db.refresh(relation)
            return relation
        except Exception as e:
            await self.db.rollback()
            raise e

    async def unlink_content(self, node_id: UUID, content_id: UUID):
        """
        Unlink a content item from a node and update node stats.
        """
        # Check relation exists
        stmt = select(ContentNodeRelation).where(
            ContentNodeRelation.node_id == node_id,
            ContentNodeRelation.content_id == content_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            return # Already unlinked

        try:
            # Delete relation
            await self.db.delete(existing)
            
            # Update node stats
            # Ensure content_count doesn't go below 0
            await self.db.execute(
                update(PyramidNode)
                .where(PyramidNode.id == node_id)
                .values(
                    content_count=func.max(0, PyramidNode.content_count - 1)
                )
            )
            
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e

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
