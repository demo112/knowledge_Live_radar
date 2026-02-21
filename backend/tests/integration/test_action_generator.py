import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.ai.processors.action_generator import ActionGenerator
from app.schemas.intent import IntentParseResult, IntentType, ActionType
from app.schemas.ai import PyramidSuggestResponse, PyramidNodeStructure
from uuid import uuid4

@pytest.mark.asyncio
async def test_generate_learn_actions():
    # Mock intent
    intent = IntentParseResult(
        original_text="I want to learn Go",
        intent_type=IntentType.LEARN,
        primary_topic="Go",
        goal="Learn Go",
        confidence=1.0
    )
    
    # Mock structure response
    mock_structure = PyramidSuggestResponse(
        suggestion_id=uuid4(),
        structure=PyramidNodeStructure(
            name="Go",
            description="Go Language",
            children=[
                PyramidNodeStructure(name="Syntax", description="Go syntax"),
                PyramidNodeStructure(name="Types", description="Go types")
            ]
        ),
        reasoning="Because Go is cool"
    )
    
    with patch("app.core.ai.processors.action_generator.pyramid_processor.generate_structure", new_callable=AsyncMock) as mock_generate_structure:
        mock_generate_structure.return_value = mock_structure
        
        generator = ActionGenerator()
        actions = await generator.generate_actions(intent)
        
        assert len(actions) == 3 # 1 Cluster + 2 Nodes
        assert actions[0].type == ActionType.CREATE_CLUSTER
        assert actions[0].parameters["name"] == "Go"
        
        assert actions[1].type == ActionType.CREATE_NODE
        assert actions[1].parameters["name"] == "Syntax"
        
        assert actions[2].type == ActionType.CREATE_NODE
        assert actions[2].parameters["name"] == "Types"

@pytest.mark.asyncio
async def test_generate_research_actions():
    # Mock intent
    intent = IntentParseResult(
        original_text="Research Quantum Computing",
        intent_type=IntentType.RESEARCH,
        primary_topic="Quantum Computing",
        goal="Deep dive",
        confidence=1.0
    )
    
    # Mock AI response for research plan
    mock_response = """
    [
        {
            "query": "Quantum Entanglement papers",
            "type": "paper",
            "description": "Find papers"
        }
    ]
    """
    
    with patch("app.core.ai.processors.action_generator.ai_client.chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response
        
        generator = ActionGenerator()
        actions = await generator.generate_actions(intent)
        
        assert len(actions) == 1
        assert actions[0].type == ActionType.SEARCH_CONTENT
        assert actions[0].parameters["query"] == "Quantum Entanglement papers"
