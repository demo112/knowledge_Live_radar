import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.services.suggestion_executor import SuggestionExecutor
from app.models.ai_suggestion import AISuggestion
from app.models.source import InformationSource, SourceNodeRelation

@pytest.mark.asyncio
async def test_execute_add_source():
    # Mock DB session
    db = AsyncMock()
    executor = SuggestionExecutor(db)
    
    # Mock Suggestion
    target_id = uuid.uuid4()
    suggestion = AISuggestion(
        id=uuid.uuid4(),
        pyramid_id=uuid.uuid4(),
        action_type="add_source",
        target_type="pyramid_node",
        target_id=target_id,
        params={
            "name": "Test Source",
            "description": "Test Description",
            "type": "web",
            "url": "http://test.com"
        }
    )
    
    # Execute
    result = await executor._execute_add_source(suggestion)
    
    # Assert
    assert result["action"] == "add_source"
    assert result["name"] == "Test Source"
    
    # Verify DB add called
    assert db.add.call_count >= 1
    
    # Verify InformationSource created correctly
    args, _ = db.add.call_args_list[0]
    source = args[0]
    assert isinstance(source, InformationSource)
    assert source.name == "Test Source"
    assert source.config.get("description") == "Test Description"
    assert source.url == "http://test.com"
    
    # Verify Relation created
    if db.add.call_count >= 2:
        args, _ = db.add.call_args_list[1]
        relation = args[0]
        assert isinstance(relation, SourceNodeRelation)
        assert relation.node_id == target_id
        assert relation.source_id == source.id
