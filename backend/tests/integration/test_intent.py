import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.intent_service import IntentService
from app.schemas.intent import IntentType, Action, ActionType, IntentCreateRequest

@pytest.mark.asyncio
async def test_parse_intent(db_session):
    # Mock AI response
    mock_response = """
    {
        "intent_type": "learn",
        "primary_topic": "React Native",
        "sub_topics": ["Architecture", "Performance"],
        "goal": "Learn React Native",
        "confidence": 0.9
    }
    """
    
    with patch("app.core.ai.processors.intent.ai_client.chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_response
        
        service = IntentService(db_session)
        text = "I want to learn about React Native"
        
        result = await service.parse_intent(text)
        
        assert result.intent_type == IntentType.LEARN
        assert result.primary_topic == "React Native"
        assert "Architecture" in result.sub_topics
        assert result.original_text == text

@pytest.mark.asyncio
async def test_process_intent(db_session):
    # Mock AI response for intent parsing
    mock_intent_response = """
    {
        "intent_type": "learn",
        "primary_topic": "Rust",
        "sub_topics": ["Ownership", "Borrowing"],
        "goal": "Learn Rust",
        "confidence": 0.95
    }
    """
    
    # Mock actions
    mock_actions = [
        Action(type=ActionType.CREATE_CLUSTER, description="Create Cluster", parameters={"name": "Rust"}),
        Action(type=ActionType.CREATE_NODE, description="Create Node", parameters={"name": "Rust"})
    ]

    with patch("app.core.ai.processors.intent.ai_client.chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_intent_response
        
        with patch("app.services.intent_service.action_generator.generate_actions", new_callable=AsyncMock) as mock_generate_actions:
            mock_generate_actions.return_value = mock_actions
            
            service = IntentService(db_session)
            request = IntentCreateRequest(text="I want to learn Rust")
            
            result = await service.process_intent(request)
            
            assert result.parsed_intent.intent_type == IntentType.LEARN
            assert len(result.suggested_actions) == 2
            assert result.suggested_actions[0].type == ActionType.CREATE_CLUSTER
