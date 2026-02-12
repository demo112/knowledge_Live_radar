import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.content_analyzer import ContentAnalyzer
from app.models.content import ContentItem
from app.models.approval import Approval

@pytest.mark.asyncio
async def test_analyze_content_success():
    mock_db = AsyncMock()
    
    # Mock ContentItem
    content_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()
    content_item = ContentItem(id=content_id, content_text="Some text")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = content_item
    mock_db.execute.return_value = mock_result

    # Mock Services
    with patch("app.services.content_analyzer.ConceptExtractor") as MockExtractor, \
         patch("app.services.content_analyzer.ConceptMatcher") as MockMatcher, \
         patch("app.services.content_analyzer.ProposalGenerator") as MockGenerator:
         
        mock_extractor = MockExtractor.return_value
        mock_matcher = MockMatcher.return_value
        mock_generator = MockGenerator.return_value
        
        # Setup returns
        mock_extractor.extract_concepts = AsyncMock(return_value=[{"name": "Concept"}])
        mock_extractor.save_concepts = AsyncMock(return_value=["SavedConcept"])
        mock_matcher.batch_match = AsyncMock(return_value=["Match"])
        mock_generator.generate_proposals_from_matches = AsyncMock(return_value=["Proposal"])
        
        analyzer = ContentAnalyzer(mock_db)
        proposals = await analyzer.analyze_content(content_id, pyramid_id)
        
        assert len(proposals) == 1
        assert proposals[0] == "Proposal"
        
        mock_extractor.extract_concepts.assert_called_once_with("Some text")
        mock_extractor.save_concepts.assert_called_once()
        mock_matcher.batch_match.assert_called_once_with(["SavedConcept"], pyramid_id)
        mock_generator.generate_proposals_from_matches.assert_called_once_with(["Match"], content_item, pyramid_id)

@pytest.mark.asyncio
async def test_analyze_content_not_found():
    mock_db = AsyncMock()
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    analyzer = ContentAnalyzer(mock_db)
    proposals = await analyzer.analyze_content(uuid.uuid4(), uuid.uuid4())
    
    assert proposals == []

@pytest.mark.asyncio
async def test_analyze_content_no_concepts():
    mock_db = AsyncMock()
    
    content_item = ContentItem(id=uuid.uuid4(), content_text="Some text")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = content_item
    mock_db.execute.return_value = mock_result
    
    with patch("app.services.content_analyzer.ConceptExtractor") as MockExtractor:
        mock_extractor = MockExtractor.return_value
        mock_extractor.extract_concepts = AsyncMock(return_value=[])
        
        analyzer = ContentAnalyzer(mock_db)
        proposals = await analyzer.analyze_content(uuid.uuid4(), uuid.uuid4())
        
        assert proposals == []
        mock_extractor.save_concepts.assert_not_called()
