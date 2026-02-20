import pytest
import uuid
import json
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.concept_extractor import ConceptExtractor
from app.services.concept_matcher import ConceptMatcher, MatchType
from app.models.concept import Concept, ConceptSynonym
from app.models.pyramid import PyramidNode

@pytest.mark.asyncio
async def test_extract_concepts():
    mock_db = AsyncMock()
    extractor = ConceptExtractor(mock_db)
    
    expected_concepts = [
        {"name": "Python", "type": "technology", "description": "Lang", "confidence": 0.9}
    ]
    
    with patch("app.services.concept_extractor.ai_facade.extract_concepts", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = expected_concepts
        
        concepts = await extractor.extract_concepts("Python is great")
        
        assert len(concepts) == 1
        assert concepts[0]["name"] == "Python"
        assert concepts[0]["type"] == "technology"

@pytest.mark.asyncio
async def test_save_concepts_new():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    # Mock execute result for existing concept check (return empty)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result
    
    extractor = ConceptExtractor(mock_db)
    
    concepts_data = [{"name": "Python", "type": "technology", "description": "Lang"}]
    saved = await extractor.save_concepts(concepts_data)
    
    assert len(saved) == 1
    assert saved[0].name == "Python"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_save_concepts_existing():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    existing_concept = Concept(id=uuid.uuid4(), name="Python", type="technology")
    
    # Mock execute result for existing concept check (return existing)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_concept
    mock_db.execute.return_value = mock_result
    
    extractor = ConceptExtractor(mock_db)
    
    concepts_data = [{"name": "Python", "type": "technology", "description": "Lang"}]
    saved = await extractor.save_concepts(concepts_data)
    
    assert len(saved) == 1
    assert saved[0].id == existing_concept.id
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_match_concept_exact():
    mock_db = AsyncMock()
    matcher = ConceptMatcher(mock_db)
    
    concept = Concept(id=uuid.uuid4(), name="Python")
    pyramid_id = uuid.uuid4()
    
    # Mock finding node
    mock_node = PyramidNode(id=uuid.uuid4(), name="Python", pyramid_id=pyramid_id)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_node
    mock_db.execute.return_value = mock_result
    
    result = await matcher.match_concept(concept, pyramid_id)
    
    assert result.match_type == MatchType.EXACT
    assert result.node_id == mock_node.id
    assert result.confidence == 1.0

@pytest.mark.asyncio
async def test_match_concept_synonym():
    mock_db = AsyncMock()
    matcher = ConceptMatcher(mock_db)
    
    concept = Concept(id=uuid.uuid4(), name="Py")
    pyramid_id = uuid.uuid4()
    
    # Mock exact match fail
    mock_result_exact = MagicMock()
    mock_result_exact.scalars.return_value.first.return_value = None
    
    # Mock finding synonyms
    mock_synonym = ConceptSynonym(id=uuid.uuid4(), concept_id=concept.id, synonym="Python")
    mock_result_synonyms = MagicMock()
    mock_result_synonyms.scalars.return_value.all.return_value = [mock_synonym]
    
    # Mock finding node by synonym
    mock_node = PyramidNode(id=uuid.uuid4(), name="Python", pyramid_id=pyramid_id)
    mock_result_node = MagicMock()
    mock_result_node.scalars.return_value.first.return_value = mock_node
    
    # Setup side effects for execute calls
    # 1. Exact match check -> None
    # 2. Get Synonyms -> [ConceptSynonym]
    # 3. Check Synonym 1 -> Node
    mock_db.execute.side_effect = [mock_result_exact, mock_result_synonyms, mock_result_node]
    
    result = await matcher.match_concept(concept, pyramid_id)
    
    assert result.match_type == MatchType.SYNONYM
    assert result.node_id == mock_node.id
    assert result.confidence == 0.9

@pytest.mark.asyncio
async def test_match_concept_new():
    mock_db = AsyncMock()
    matcher = ConceptMatcher(mock_db)
    
    concept = Concept(id=uuid.uuid4(), name="NewThing")
    pyramid_id = uuid.uuid4()
    
    # All queries return nothing
    mock_result_empty = MagicMock()
    mock_result_empty.scalars.return_value.first.return_value = None
    mock_result_empty.scalars.return_value.all.return_value = []
    
    mock_db.execute.return_value = mock_result_empty
    
    result = await matcher.match_concept(concept, pyramid_id)
    
    assert result.match_type == MatchType.NEW
    assert result.node_id is None
