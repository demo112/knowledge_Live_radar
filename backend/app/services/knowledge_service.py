from typing import List, Optional, Any, Union
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func

from app.repositories.knowledge import KnowledgeNodeRepository, KnowledgeClusterRepository, KnowledgeRelationRepository
from app.models.knowledge import KnowledgeNode, KnowledgeCluster, KnowledgeNodeRelation, ClusterNodeMembership
from app.models.content import ContentKnowledgeRelation
from app.models.concept import Concept
from app.core.ai.facade import ai_facade
from app.schemas.knowledge import (
    KnowledgeNodeCreate, KnowledgeNodeUpdate,
    KnowledgeClusterCreate, KnowledgeClusterUpdate,
    KnowledgeNodeRelationCreate, ClusterNodeMembershipCreate
)

class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.node_repo = KnowledgeNodeRepository(db)
        self.cluster_repo = KnowledgeClusterRepository(db)
        self.relation_repo = KnowledgeRelationRepository(db)

    # Node Operations
    async def create_node(self, data: KnowledgeNodeCreate) -> KnowledgeNode:
        existing = await self.node_repo.get_by_name(data.name)
        if existing:
            raise HTTPException(status_code=400, detail=f"Node with name '{data.name}' already exists")
        
        node = await self.node_repo.create(data.model_dump())
        return node

    async def get_node(self, node_id: UUID) -> Optional[KnowledgeNode]:
        node = await self.node_repo.get_with_relations(node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Knowledge Node not found")
        return node

    async def update_node(self, node_id: UUID, data: Union[KnowledgeNodeUpdate, dict] = None, **kwargs) -> KnowledgeNode:
        node = await self.get_node(node_id)
        update_data = {}
        if data:
            if isinstance(data, KnowledgeNodeUpdate):
                update_data = data.model_dump(exclude_unset=True)
            else:
                update_data = data
        
        if kwargs:
            update_data.update(kwargs)
            
        updated_node = await self.node_repo.update(node, update_data)
        return updated_node

    async def delete_node(self, node_id: UUID) -> bool:
        await self.get_node(node_id)
        await self.node_repo.soft_delete(node_id)
        return True

    async def list_nodes(self, skip: int = 0, limit: int = 100) -> List[KnowledgeNode]:
        return await self.node_repo.get_all(skip=skip, limit=limit)

    async def generate_cognitive_model_for_node(self, node_id: UUID) -> KnowledgeNode:
        """
        Task 2.1: Cognitive Model Generation
        Generate a structured cognitive model for a node using AI.
        Integrate Concept table data if available.
        """
        node = await self.get_node(node_id)
        
        # 1. Prepare context from existing Concept
        context = ""
        concept = None
        
        if node.concept_id:
            stmt = select(Concept).where(Concept.id == node.concept_id)
            result = await self.db.execute(stmt)
            concept = result.scalar_one_or_none()
        else:
            # Try to match existing concept by name
            stmt = select(Concept).where(Concept.name == node.name)
            result = await self.db.execute(stmt)
            concept = result.scalar_one_or_none()
            if concept:
                node.concept_id = concept.id
                
        if concept:
            context += f"Concept Type: {concept.type}\n"
            if concept.description:
                context += f"Concept Description: {concept.description}\n"
                
        # 2. Generate model via AI
        cognitive_model = await ai_facade.generate_cognitive_model(
            name=node.name,
            description=node.description or "",
            context=context
        )
        
        # 3. Update node
        node.ai_model = cognitive_model
        
        # 4. If concept doesn't exist, maybe create one? 
        # For now, we focus on populating the node's ai_model.
        
        await self.db.commit()
        # Re-fetch the node to ensure all relationships are loaded and attributes are fresh
        # This avoids issues with expired attributes after commit
        node = await self.get_node(node_id)
        return node

    # Cluster Operations
    async def create_cluster(self, data: KnowledgeClusterCreate) -> KnowledgeCluster:
        cluster = await self.cluster_repo.create(data.model_dump())
        return cluster

    async def get_cluster(self, cluster_id: UUID) -> Optional[KnowledgeCluster]:
        cluster = await self.cluster_repo.get_with_members(cluster_id)
        if not cluster:
            raise HTTPException(status_code=404, detail="Knowledge Cluster not found")
        return cluster

    async def update_cluster(self, cluster_id: UUID, data: KnowledgeClusterUpdate) -> KnowledgeCluster:
        cluster = await self.get_cluster(cluster_id)
        updated_cluster = await self.cluster_repo.update(cluster, data.model_dump(exclude_unset=True))
        return updated_cluster

    async def delete_cluster(self, cluster_id: UUID) -> bool:
        cluster = await self.get_cluster(cluster_id)
        # Assuming status update for soft delete or direct delete
        await self.cluster_repo.update(cluster, {"status": "archived"})
        return True

    async def list_clusters(self, skip: int = 0, limit: int = 100) -> List[KnowledgeCluster]:
        return await self.cluster_repo.get_all(skip=skip, limit=limit)

    # Membership Operations
    async def add_node_to_cluster(self, cluster_id: UUID, data: ClusterNodeMembershipCreate) -> ClusterNodeMembership:
        await self.get_cluster(cluster_id)
        await self.get_node(data.node_id)
        
        # Check if membership exists
        stmt = select(ClusterNodeMembership).where(
            and_(
                ClusterNodeMembership.cluster_id == cluster_id,
                ClusterNodeMembership.node_id == data.node_id
            )
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Node is already a member of this cluster")

        membership = ClusterNodeMembership(
            cluster_id=cluster_id,
            **data.model_dump()
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def remove_node_from_cluster(self, cluster_id: UUID, node_id: UUID) -> bool:
        stmt = select(ClusterNodeMembership).where(
            and_(
                ClusterNodeMembership.cluster_id == cluster_id,
                ClusterNodeMembership.node_id == node_id
            )
        )
        result = await self.db.execute(stmt)
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise HTTPException(status_code=404, detail="Membership not found")
            
        await self.db.delete(membership)
        await self.db.commit()
        return True

    # Relation Operations
    async def create_relation(self, source_id: UUID, data: KnowledgeNodeRelationCreate) -> KnowledgeNodeRelation:
        await self.get_node(source_id)
        await self.get_node(data.target_node_id)
        
        relation = await self.relation_repo.create({
            "source_node_id": source_id,
            **data.model_dump()
        })
        return relation

    async def delete_relation(self, relation_id: UUID) -> bool:
        await self.relation_repo.delete(relation_id)
        return True

    # Content Linking Operations
    async def link_content(self, node_id: UUID, content_id: UUID, source: str = "manual", confidence: float = 1.0) -> ContentKnowledgeRelation:
        """
        Link a content item to a knowledge node and update node stats.
        """
        # Check node exists
        node = await self.get_node(node_id)
        
        # Check if relation already exists
        stmt = select(ContentKnowledgeRelation).where(
            and_(
                ContentKnowledgeRelation.node_id == node_id,
                ContentKnowledgeRelation.content_id == content_id
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing

        try:
            # Create relation
            relation = ContentKnowledgeRelation(
                node_id=node_id,
                content_id=content_id,
                source=source,
                confidence=confidence
            )
            self.db.add(relation)
            
            # Update node stats
            await self.db.execute(
                update(KnowledgeNode)
                .where(KnowledgeNode.id == node_id)
                .values(
                    content_count=KnowledgeNode.content_count + 1,
                    last_content_at=func.now()
                )
            )
            
            await self.db.commit()
            await self.db.refresh(relation)
            return relation
        except Exception as e:
            await self.db.rollback()
            raise e

    async def unlink_content(self, node_id: UUID, content_id: UUID) -> bool:
        """
        Unlink a content item from a knowledge node and update node stats.
        """
        # Check relation exists
        stmt = select(ContentKnowledgeRelation).where(
            and_(
                ContentKnowledgeRelation.node_id == node_id,
                ContentKnowledgeRelation.content_id == content_id
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            return True # Already unlinked

        try:
            # Delete relation
            await self.db.delete(existing)
            
            # Update node stats
            await self.db.execute(
                update(KnowledgeNode)
                .where(KnowledgeNode.id == node_id)
                .values(
                    content_count=func.max(0, KnowledgeNode.content_count - 1)
                )
            )
            
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise e
