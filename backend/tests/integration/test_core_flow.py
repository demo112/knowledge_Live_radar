import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.content_analyzer import ContentAnalyzer
from app.services.approval_service import ApprovalService
from app.services.decision_executor import DecisionExecutor
from app.models.approval import Approval
from app.models.pyramid import PyramidNode

@pytest.mark.asyncio
async def test_core_flow():
    # 1. Setup Mocks
    mock_db = AsyncMock()
    
    # Mock data
    content_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    
    # Mock ContentItem
    mock_content_item = MagicMock()
    mock_content_item.content_text = "Some content about AI"
    mock_content_item.id = content_id
    
    # Setup db.execute for ContentAnalyzer
    # It calls execute(select(ContentItem))
    mock_result_content = MagicMock()
    mock_result_content.scalar_one_or_none.return_value = mock_content_item
    
    mock_db.execute.return_value = mock_result_content
    
    # 2. Test ContentAnalyzer (Mocking internal dependencies)
    with patch("app.services.content_analyzer.ConceptExtractor") as MockExtractor, \
         patch("app.services.content_analyzer.ConceptMatcher") as MockMatcher, \
         patch("app.services.content_analyzer.ProposalGenerator") as MockGenerator:
         
        # Setup analyzer chain return values
        MockExtractor.return_value.extract_concepts = AsyncMock(return_value=["concept1"])
        MockExtractor.return_value.save_concepts = AsyncMock(return_value=[MagicMock(id="c1", name="concept1")])
        MockMatcher.return_value.batch_match = AsyncMock(return_value=[{"concept": "concept1", "match": "node1"}])
        
        expected_proposals = [
                Approval(
                    id=proposal_id,
                    type="create_node",
                    status="pending",
                    data={"name": "New Node", "pyramid_id": str(pyramid_id)}
                )
            ]
        MockGenerator.return_value.generate_proposals_from_matches = AsyncMock(return_value=expected_proposals)
        
        analyzer = ContentAnalyzer(mock_db)
        proposals = await analyzer.analyze_content(content_id, pyramid_id)
        
        assert len(proposals) == 1
        assert proposals[0].id == proposal_id
        
    # 3. Test ApprovalService (Review)
    approval_service = ApprovalService(mock_db)
    
    # Mock get_approval to return our proposal
    mock_approval = proposals[0]
    
    # Reset mock_db.execute for subsequent calls
    mock_result_approval = MagicMock()
    mock_result_approval.scalar_one_or_none.return_value = mock_approval
    mock_db.execute.return_value = mock_result_approval
    
    # Review: Approve
    updated_approval = await approval_service.review_approval(
        proposal_id, 
        MagicMock(model_dump=lambda **kwargs: {"status": "approved", "reviewer_id": "admin"})
    )
    
    assert updated_approval.status == "approved"
    
    # 4. Test DecisionExecutor (Execute)
    with patch("app.services.decision_executor.SnapshotService") as MockSnapshotService, \
         patch("app.services.notification_service.notification_service") as mock_notification:
        
        mock_snapshot_instance = MockSnapshotService.return_value
        mock_snapshot_instance.create_snapshot = AsyncMock()
        
        # Configure notification service mock
        mock_notification.notify_approval_status_change = AsyncMock()
        
        # Configure db.add to be synchronous
        mock_db.add = MagicMock()
        
        executor = DecisionExecutor(mock_db)
        
        # Ensure db.execute returns the approved approval when queried
        # The executor calls db.execute(select(Approval))
        mock_result_exec = MagicMock()
        mock_result_exec.scalar_one_or_none.return_value = mock_approval
        mock_db.execute.return_value = mock_result_exec
        
        success = await executor.execute_approval(proposal_id, "admin")
        
        assert success is True
        assert mock_approval.status == "executed"
        
        # Verify Snapshot was created
        mock_snapshot_instance.create_snapshot.assert_called_once()
        
        # Verify Notification was sent
        mock_notification.notify_approval_status_change.assert_called_once()
        
        # Verify DB commit was called
        assert mock_db.commit.call_count >= 1
