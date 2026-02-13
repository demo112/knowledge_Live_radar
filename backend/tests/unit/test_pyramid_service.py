import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidNodeCreate

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def pyramid_service(mock_db_session):
    # Patch the repositories at the class level where they are imported
    with patch("app.services.pyramid_service.PyramidRepository") as MockPyramidRepo, \
         patch("app.services.pyramid_service.PyramidNodeRepository") as MockNodeRepo:
        
        service = PyramidService(mock_db_session)
        service.pyramid_repo = AsyncMock()
        service.node_repo = AsyncMock()
        yield service

@pytest.mark.asyncio
async def test_create_pyramid(pyramid_service):
    schema = PyramidCreate(name="Test Pyramid", description="Desc")
    expected_pyramid = {"id": uuid4(), "name": "Test Pyramid"}
    
    pyramid_service.pyramid_repo.create.return_value = expected_pyramid
    
    result = await pyramid_service.create_pyramid(schema)
    
    assert result == expected_pyramid
    pyramid_service.pyramid_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_pyramid_found(pyramid_service):
    pyramid_id = uuid4()
    mock_pyramid = MagicMock()
    mock_pyramid.id = pyramid_id
    mock_pyramid.is_deleted = False
    
    pyramid_service.pyramid_repo.get.return_value = mock_pyramid
    
    result = await pyramid_service.get_pyramid(pyramid_id)
    assert result == mock_pyramid

@pytest.mark.asyncio
async def test_get_pyramid_not_found(pyramid_service):
    pyramid_id = uuid4()
    pyramid_service.pyramid_repo.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await pyramid_service.get_pyramid(pyramid_id)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_pyramid_deleted(pyramid_service):
    pyramid_id = uuid4()
    mock_pyramid = MagicMock()
    mock_pyramid.is_deleted = True
    
    pyramid_service.pyramid_repo.get.return_value = mock_pyramid
    
    with pytest.raises(HTTPException) as exc:
        await pyramid_service.get_pyramid(pyramid_id)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_calculate_health_score_empty(pyramid_service):
    pyramid_id = uuid4()
    mock_pyramid = MagicMock()
    mock_pyramid.is_deleted = False
    mock_pyramid.nodes = []
    
    pyramid_service.pyramid_repo.get_with_nodes.return_value = mock_pyramid
    
    score = await pyramid_service.calculate_health_score(pyramid_id)
    assert score == 100

@pytest.mark.asyncio
async def test_calculate_health_score_partial(pyramid_service):
    pyramid_id = uuid4()
    mock_pyramid = MagicMock()
    mock_pyramid.is_deleted = False
    
    node1 = MagicMock()
    node1.status = "completed"
    node2 = MagicMock()
    node2.status = "pending"
    
    mock_pyramid.nodes = [node1, node2]
    
    pyramid_service.pyramid_repo.get_with_nodes.return_value = mock_pyramid
    
    score = await pyramid_service.calculate_health_score(pyramid_id)
    assert score == 50

@pytest.mark.asyncio
async def test_add_node_root(pyramid_service):
    pyramid_id = uuid4()
    schema = PyramidNodeCreate(name="Root Node")
    
    # Mock get_pyramid success
    mock_pyramid = MagicMock()
    mock_pyramid.is_deleted = False
    pyramid_service.pyramid_repo.get.return_value = mock_pyramid
    
    expected_node = {"id": uuid4(), "name": "Root Node", "path": "/"}
    pyramid_service.node_repo.create.return_value = expected_node
    
    result = await pyramid_service.add_node(pyramid_id, schema)
    
    assert result == expected_node
    # Verify create called with correct data
    call_args = pyramid_service.node_repo.create.call_args[0][0]
    assert call_args["level"] == 0
    assert call_args["path"] == "/"
    assert call_args["pyramid_id"] == pyramid_id

@pytest.mark.asyncio
async def test_add_node_child(pyramid_service):
    pyramid_id = uuid4()
    parent_id = uuid4()
    schema = PyramidNodeCreate(name="Child Node", parent_id=parent_id)
    
    # Mock get_pyramid
    mock_pyramid = MagicMock()
    mock_pyramid.is_deleted = False
    pyramid_service.pyramid_repo.get.return_value = mock_pyramid
    
    # Mock parent node
    mock_parent = MagicMock()
    mock_parent.id = parent_id
    mock_parent.pyramid_id = pyramid_id
    mock_parent.level = 0
    mock_parent.path = "/"
    
    pyramid_service.node_repo.get.return_value = mock_parent
    
    expected_node = {"id": uuid4(), "name": "Child Node", "path": f"/{parent_id}/"}
    pyramid_service.node_repo.create.return_value = expected_node
    
    result = await pyramid_service.add_node(pyramid_id, schema)
    
    assert result == expected_node
    
    call_args = pyramid_service.node_repo.create.call_args[0][0]
    assert call_args["level"] == 1
    assert call_args["path"] == f"/{parent_id}/"

@pytest.mark.asyncio
async def test_add_node_invalid_parent(pyramid_service):
    pyramid_id = uuid4()
    parent_id = uuid4()
    schema = PyramidNodeCreate(name="Child Node", parent_id=parent_id)
    
    # Mock get_pyramid
    pyramid_service.pyramid_repo.get.return_value = MagicMock(is_deleted=False)
    
    # Parent not found
    pyramid_service.node_repo.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await pyramid_service.add_node(pyramid_id, schema)
    assert exc.value.status_code == 404
