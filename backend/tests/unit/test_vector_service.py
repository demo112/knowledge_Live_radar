import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from app.services.vector_service import VectorService

@pytest.fixture
def mock_chroma_client():
    with patch("app.services.vector_service.chromadb.PersistentClient") as mock_client:
        yield mock_client

@pytest.fixture
def mock_embedding_fn():
    with patch("app.services.vector_service.embedding_functions.SentenceTransformerEmbeddingFunction") as mock_fn:
        yield mock_fn

@pytest.fixture
def vector_service(mock_chroma_client, mock_embedding_fn):
    return VectorService()

@pytest.mark.asyncio
async def test_upsert_node_vector(vector_service):
    node_id = uuid4()
    name = "Test Node"
    description = "Test Description"
    
    await vector_service.upsert_node_vector(node_id, name, description)
    
    vector_service.node_collection.upsert.assert_called_once()
    call_args = vector_service.node_collection.upsert.call_args
    assert call_args.kwargs['ids'] == [str(node_id)]
    assert call_args.kwargs['documents'] == [f"{name}: {description}"]
    assert call_args.kwargs['metadatas'][0]['type'] == 'node'

@pytest.mark.asyncio
async def test_upsert_content_vector(vector_service):
    content_id = uuid4()
    title = "Test Content"
    summary = "Test Summary"
    concepts = ["concept1", "concept2"]
    
    await vector_service.upsert_content_vector(content_id, title, summary, concepts)
    
    vector_service.content_collection.upsert.assert_called_once()
    call_args = vector_service.content_collection.upsert.call_args
    assert call_args.kwargs['ids'] == [str(content_id)]
    assert "Test Summary" in call_args.kwargs['documents'][0]
    assert "concept1, concept2" in call_args.kwargs['documents'][0]
    assert call_args.kwargs['metadatas'][0]['type'] == 'content'

@pytest.mark.asyncio
async def test_search_similar_nodes(vector_service):
    id1 = str(uuid4())
    id2 = str(uuid4())
    
    # Mock query return
    vector_service.node_collection.query.return_value = {
        "ids": [[id1, id2]],
        "distances": [[0.1, 0.2]],
        "metadatas": [[{"name": "Node 1"}, {"name": "Node 2"}]]
    }
    
    results = await vector_service.search_similar_nodes("query", limit=2)
    
    assert len(results) == 2
    assert str(results[0]["id"]) == id1
    assert results[0]["distance"] == 0.1
    assert results[0]["metadata"]["name"] == "Node 1"
