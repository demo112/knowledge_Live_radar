import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.approval_service import ApprovalService
from app.schemas.approval import BatchReviewRequest, CleanupRequest
from app.models.approval import Approval

@pytest.mark.asyncio
async def test_batch_review_approve():
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    
    # Mock existing approvals
    approval1 = Approval(id=id1, status="pending")
    approval2 = Approval(id=id2, status="pending")
    
    # Mock get_approval to return based on id
    async def mock_get_approval(id):
        if id == id1:
            return approval1
        if id == id2:
            return approval2
        return None
    
    service.get_approval = AsyncMock(side_effect=mock_get_approval)
    
    request = BatchReviewRequest(ids=[id1, id2], action="approve", reason="Batch approve")
    
    result = await service.batch_review(request)
    
    assert result.success_count == 2
    assert result.failure_count == 0
    assert approval1.status == "approved"
    assert approval2.status == "approved"
    assert mock_session.commit.called

@pytest.mark.asyncio
async def test_batch_review_reject_delete():
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    
    id1 = uuid.uuid4()
    
    approval1 = Approval(id=id1, status="pending")
    
    async def mock_get_approval(id):
        if id == id1:
            return approval1
        return None
    
    service.get_approval = AsyncMock(side_effect=mock_get_approval)
    
    request = BatchReviewRequest(ids=[id1], action="reject", reason="Batch reject")
    
    result = await service.batch_review(request)
    
    assert result.success_count == 1
    assert result.failure_count == 0
    
    # Verify deletion
    mock_session.delete.assert_called_with(approval1)
    mock_session.commit.assert_called()

@pytest.mark.asyncio
async def test_batch_review_partial_failure():
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    
    id1 = uuid.uuid4()
    id2 = uuid.uuid4() # Not exists
    
    approval1 = Approval(id=id1, status="pending")
    
    async def mock_get_approval(id):
        if id == id1:
            return approval1
        return None
    
    service.get_approval = AsyncMock(side_effect=mock_get_approval)
    
    request = BatchReviewRequest(ids=[id1, id2], action="approve", reason="Batch partial")
    
    result = await service.batch_review(request)
    
    assert result.success_count == 1
    assert result.failure_count == 1
    assert result.failures[0]['id'] == str(id2)
    assert approval1.status == "approved"

@pytest.mark.asyncio
async def test_cleanup_pending_approvals():
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    
    # Mock get_approvals to return list of pending approvals
    approval1 = Approval(id=uuid.uuid4(), status="pending")
    approval2 = Approval(id=uuid.uuid4(), status="pending")
    
    # We need to mock the execute result for the select query in cleanup
    # But since we are mocking at service level logic or db level?
    # Ideally we mock DB execution.
    
    # Let's mock the select execution to return these approvals
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [approval1, approval2]
    mock_session.execute.return_value = mock_result
    
    request = CleanupRequest(reason="Cleanup test")
    
    result = await service.cleanup_pending_approvals(request)
    
    assert result.count == 2
    assert mock_session.delete.call_count == 2
    mock_session.commit.assert_called()
