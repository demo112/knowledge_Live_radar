
import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.knowledge_service import KnowledgeService
from app.services.vector_service import VectorService
from app.schemas.knowledge import KnowledgeNodeCreate
from app.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_knowledge_node_vector_sync():
    async with AsyncSessionLocal() as db:
        knowledge_service = KnowledgeService(db)
        vector_service = VectorService()
        
        # 1. Create a KnowledgeNode
        node_name = f"Test Node {uuid4()}"
        node_data = KnowledgeNodeCreate(
            name=node_name,
            description="A test node for vector sync",
            node_type="concept",
            status="active"
        )
        node = await knowledge_service.create_node(node_data)
        
        # 2. Search for it immediately
        results = await vector_service.search_similar_nodes(
            query_text=node_name,
            limit=1,
            node_type="knowledge_node"
        )
        
        # 3. Assert it was found
        found = False
        for res in results:
            if str(res["id"]) == str(node.id):
                found = True
                break
        
        assert found, f"KnowledgeNode {node.id} ({node_name}) was not found in VectorDB after creation"
