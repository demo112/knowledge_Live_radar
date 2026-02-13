import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.pyramid import Pyramid, PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from unittest.mock import AsyncMock, MagicMock

# Mock VectorService to avoid installing torch/sentence-transformers in CI/Test env if network fails
class MockVectorService:
    def __init__(self):
        pass
    
    async def upsert_content_vector(self, *args, **kwargs):
        pass
        
    async def upsert_node_vector(self, *args, **kwargs):
        pass
        
    async def search_similar_nodes(self, query_text, limit=3):
        return []
    
    async def delete_node_vector(self, *args, **kwargs):
        pass
        
    async def delete_content_vector(self, *args, **kwargs):
        pass

@pytest.mark.asyncio
async def test_evolution_flow(client: AsyncClient, db_session: AsyncSession, monkeypatch):
    # 1. Create Pyramid and Node
    pyramid_id = uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid")
    db_session.add(pyramid)
    
    node_id = uuid4()
    # Name matches content title for similarity
    node = PyramidNode(
        id=node_id, 
        pyramid_id=pyramid_id, 
        name="Artificial Intelligence", 
        content_count=0,
        path="/",
        level=0
    ) 
    db_session.add(node)
    
    # 2. Create ContentItem
    content_id = uuid4()
    content = ContentItem(
        id=content_id,
        title="Artificial Intelligence Overview",
        url="http://example.com/ai",
        summary="A comprehensive guide to Artificial Intelligence.",
        concepts=["Artificial Intelligence", "Machine Learning"],
        status="PROCESSED",
        ai_processed=True
    )
    db_session.add(content)
    await db_session.commit()
    
    # 3. Mock VectorService
    mock_vector_service = MockVectorService()
    # Mock search result to return our node
    mock_vector_service.search_similar_nodes = AsyncMock(return_value=[
        {"id": node_id, "distance": 0.1, "metadata": {}}
    ])
    
    # Patch EvolutionEngine's vector_service
    monkeypatch.setattr("app.services.evolution_engine.VectorService", lambda: mock_vector_service)
    
    # 4. Call Auto-classify API
    response = await client.post(f"/api/v1/evolution/classify/{content_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == 1 # Should match 1 node
    
    # 5. Verify Database State
    # Re-fetch node
    result = await db_session.execute(select(PyramidNode).where(PyramidNode.id == node_id))
    updated_node = result.scalar_one()
    
    # Check relation
    result = await db_session.execute(select(ContentNodeRelation).where(ContentNodeRelation.content_id == content_id))
    relation = result.scalar_one_or_none()
    
    assert relation is not None
    assert updated_node.content_count == 1
    assert relation.node_id == node_id
    assert relation.source == "ai_auto"

    # 6. Test Manual Link API
    # (Existing relation should just return success)
    response = await client.post(f"/api/v1/nodes/{node_id}/contents/{content_id}")
    assert response.status_code == 200
    
    # 7. Test Get Node Contents API
    response = await client.get(f"/api/v1/nodes/{node_id}/contents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(content_id)
    assert data["data"][0]["relation_source"] == "ai_auto"
    
    # 8. Test Unlink API
    response = await client.delete(f"/api/v1/nodes/{node_id}/contents/{content_id}")
    assert response.status_code == 200
    
    await db_session.refresh(updated_node)
    assert updated_node.content_count == 0
