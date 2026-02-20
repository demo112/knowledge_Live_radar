
import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.proposal_generator import ProposalGenerator
from app.models.content import ContentItem
from app.models.approval import Approval
from app.models.pyramid import PyramidNode
from app.services.concept_matcher import MatchResult, MatchType

# Mock objects
class MockPlacementResponse:
    def __init__(self, best_parent_id, reasoning):
        self.best_parent_id = best_parent_id
        self.reasoning = reasoning

@pytest.mark.asyncio
async def test_create_proposal_for_match_new_node_with_parent():
    mock_db = AsyncMock()
    
    pyramid_id = uuid.uuid4()
    content_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    
    content_item = ContentItem(
        id=content_id,
        title="Test Content",
        summary="Summary",
        url="http://example.com"
    )
    
    match = MatchResult(
        concept_id=uuid.uuid4(),
        match_type=MatchType.NEW,
        concept_name="New Concept",
        details="No matching node found",
        confidence=0.9
    )
    
    # Mock Repository
    with patch("app.services.proposal_generator.PyramidNodeRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        # Use AsyncMock for async methods
        mock_repo_instance.get_by_pyramid = AsyncMock()
        
        existing_node = PyramidNode(id=uuid.uuid4(), name="Existing Node", description="Desc")
        mock_repo_instance.get_by_pyramid.return_value = [existing_node]
        
        # Mock AI Facade
        with patch("app.services.proposal_generator.ai_facade") as mock_ai_facade:
            # Mock find_best_parent_node
            mock_ai_facade.find_best_parent_node = AsyncMock()
            mock_placement = MockPlacementResponse(parent_id, "Best fit logic")
            mock_ai_facade.find_best_parent_node.return_value = mock_placement
            
            # Mock generate_proposal_reason
            mock_ai_facade.generate_proposal_reason = AsyncMock()
            mock_ai_facade.generate_proposal_reason.return_value = "AI Reason"
            
            generator = ProposalGenerator(mock_db)
            
            # Call the method
            # Note: create_proposal_for_match is likely a method of generator
            # But wait, looking at file content earlier, it seemed to be inside generate_proposals_from_matches loop?
            # Or is it a standalone method?
            # Let's assume it's a method or we test generate_proposals_from_matches
            
            # Let's check ProposalGenerator structure again
            # I'll use generate_proposals_from_matches with a list of matches
            
            proposals = await generator.generate_proposals_from_matches(
                matches=[match],
                content_item=content_item,
                pyramid_id=pyramid_id
            )
            
            assert len(proposals) == 1
            approval = proposals[0]
            
            assert approval.type == "create_node"
            assert approval.data["parent_id"] == str(parent_id)
            assert "Placement: Best fit logic" in approval.reason
            assert approval.data["name"] == "New Concept"
            assert approval.data["description"] == "Extracted from content"
            
            mock_ai_facade.find_best_parent_node.assert_called_once()
            args, kwargs = mock_ai_facade.find_best_parent_node.call_args
            assert kwargs['new_node_name'] == "New Concept"
            assert len(kwargs['candidate_nodes']) == 1
            assert kwargs['candidate_nodes'][0]['id'] == str(existing_node.id)

