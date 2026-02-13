import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from app.services.evolution_engine import EvolutionEngine
from app.models.content import ContentItem

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_vector_service():
    with patch("app.services.evolution_engine.VectorService") as mock_cls:
        instance = mock_cls.return_value
        instance.upsert_content_vector = AsyncMock()
        instance.search_similar_nodes = AsyncMock()
        yield instance

@pytest.fixture
def mock_node_service():
    with patch("app.services.evolution_engine.NodeService") as mock_cls:
        instance = mock_cls.return_value
        instance.link_content = AsyncMock()
        yield instance

@pytest.fixture
def evolution_engine(mock_db, mock_vector_service, mock_node_service):
    engine = EvolutionEngine(mock_db)
    # Ensure the instances are the mocks we expect
    engine.vector_service = mock_vector_service
    engine.node_service = mock_node_service
    return engine

@pytest.mark.asyncio
async def test_auto_classify_content_match(evolution_engine, mock_vector_service, mock_node_service):
    content = ContentItem(
        id=uuid4(),
        title="Test Title",
        summary="Test Summary",
        concepts=["c1"]
    )
    
    node_id = uuid4()
    
    # Mock vector service response (low distance = match)
    mock_vector_service.search_similar_nodes.return_value = [
        {"id": node_id, "distance": 0.1, "metadata": {}}
    ]
    
    count = await evolution_engine.auto_classify_content(content)
    
    assert count == 1
    mock_vector_service.upsert_content_vector.assert_called_once()
    mock_vector_service.search_similar_nodes.assert_called_once()
    mock_node_service.link_content.assert_called_once()
    
    args = mock_node_service.link_content.call_args.kwargs
    assert args['node_id'] == node_id
    assert args['content_id'] == content.id
    assert args['source'] == "ai_auto"
    assert args['confidence'] > 0.8

@pytest.mark.asyncio
async def test_auto_classify_content_no_match(evolution_engine, mock_vector_service, mock_node_service):
    content = ContentItem(
        id=uuid4(),
        title="Test Title"
    )
    
    # Mock vector service response (high distance = no match)
    mock_vector_service.search_similar_nodes.return_value = [
        {"id": uuid4(), "distance": 0.9, "metadata": {}}
    ]
    
    count = await evolution_engine.auto_classify_content(content)
    
    assert count == 0
    mock_node_service.link_content.assert_not_called()
