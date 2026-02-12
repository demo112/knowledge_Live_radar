import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.decision_executor import DecisionExecutor
from app.models.approval import Approval
from app.models.pyramid import PyramidNode

@pytest.mark.asyncio
async def test_execute_approval_success_create_node():
    mock_db = AsyncMock()
    
    approval_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()
    
    approval = Approval(
        id=approval_id,
        status="approved",
        type="create_node",
        data={
            "pyramid_id": str(pyramid_id),
            "name": "New Node",
            "description": "Desc"
        }
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = approval
    mock_db.execute.return_value = mock_result
    mock_db.add = MagicMock()
    
    with patch("app.services.decision_executor.SnapshotService") as MockSnapshotService:
        mock_snapshot_service = MockSnapshotService.return_value
        mock_snapshot_service.create_snapshot = AsyncMock()
        
        executor = DecisionExecutor(mock_db)
        success = await executor.execute_approval(approval_id, "user1")
        
        assert success is True
        assert approval.status == "executed"
        
        mock_snapshot_service.create_snapshot.assert_called_once()
        mock_db.add.assert_called_once() # Should add new PyramidNode
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_execute_approval_not_approved():
    mock_db = AsyncMock()
    approval = Approval(id=uuid.uuid4(), status="pending")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = approval
    mock_db.execute.return_value = mock_result
    
    executor = DecisionExecutor(mock_db)
    success = await executor.execute_approval(approval.id, "user1")
    
    assert success is False
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_execute_approval_link_content():
    mock_db = AsyncMock()
    approval_id = uuid.uuid4()
    node_id = uuid.uuid4()
    content_id = uuid.uuid4()
    
    approval = Approval(
        id=approval_id,
        status="approved",
        type="link_content",
        data={
            "node_id": str(node_id),
            "content_id": str(content_id)
        }
    )
    
    # Mock finding approval
    mock_result_approval = MagicMock()
    mock_result_approval.scalar_one_or_none.return_value = approval
    
    # Mock finding node (for snapshot pyramid_id resolution)
    mock_node = PyramidNode(id=node_id, pyramid_id=uuid.uuid4())
    mock_result_node = MagicMock()
    mock_result_node.scalar_one_or_none.return_value = mock_node
    
    # Mock checking existing relation (return None)
    mock_result_relation = MagicMock()
    mock_result_relation.scalar_one_or_none.return_value = None
    
    mock_db.execute.side_effect = [mock_result_approval, mock_result_node, mock_result_relation]
    mock_db.add = MagicMock()
    
    with patch("app.services.decision_executor.SnapshotService") as MockSnapshotService:
        mock_snapshot_service = MockSnapshotService.return_value
        mock_snapshot_service.create_snapshot = AsyncMock()
        
        executor = DecisionExecutor(mock_db)
        success = await executor.execute_approval(approval_id, "user1")
        
        assert success is True
        mock_db.add.assert_called_once() # Should add ContentNodeRelation
