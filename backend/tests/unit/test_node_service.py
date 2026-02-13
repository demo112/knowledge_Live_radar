import pytest
from unittest.mock import MagicMock, AsyncMock, ANY
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.node_service import NodeService
from app.models.pyramid import PyramidNode
from app.models.content import ContentNodeRelation

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def node_service(mock_db):
    service = NodeService(mock_db)
    service.node_repo = AsyncMock() # Mock the repository
    return service

@pytest.mark.asyncio
async def test_link_content_success(node_service, mock_db):
    node_id = uuid4()
    content_id = uuid4()
    
    # Mock node exists
    node_service.node_repo.get.return_value = PyramidNode(id=node_id, content_count=0)
    
    # Mock relation not exists (execute returns None for scalar_one_or_none)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Run
    await node_service.link_content(node_id, content_id)
    
    # Verify relation added
    mock_db.add.assert_called_once()
    args = mock_db.add.call_args[0][0]
    assert isinstance(args, ContentNodeRelation)
    assert args.node_id == node_id
    assert args.content_id == content_id
    
    # Verify commit
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_unlink_content_success(node_service, mock_db):
    node_id = uuid4()
    content_id = uuid4()
    
    # Mock relation exists
    relation = ContentNodeRelation(node_id=node_id, content_id=content_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = relation
    mock_db.execute.return_value = mock_result
    
    # Run
    await node_service.unlink_content(node_id, content_id)
    
    # Verify delete
    mock_db.delete.assert_called_once_with(relation)
    
    # Verify commit
    mock_db.commit.assert_called_once()
