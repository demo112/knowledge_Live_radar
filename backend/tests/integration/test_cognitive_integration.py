import pytest
from unittest.mock import patch, MagicMock
from app.core.ai.facade import ai_facade
from app.core.ai.client import ai_client

@pytest.mark.asyncio
async def test_generate_cognitive_model_integration():
    """
    Test the integration of CognitiveProcessor through AIFacade.
    Mocks the AI client to avoid real API calls.
    """
    
    # Mock data
    mock_response_content = """
    {
        "definition": "A test concept definition.",
        "key_attributes": ["attr1", "attr2"],
        "related_concepts": ["concept1", "concept2"],
        "misconceptions": ["wrong1"],
        "evolution_path": ["step1", "step2"]
    }
    """
    
    # Mock the ai_client.chat_completion method
    with patch.object(ai_client, 'chat_completion', return_value=mock_response_content) as mock_chat:
        
        # Call the facade method
        result = await ai_facade.generate_cognitive_model(
            name="Test Concept",
            description="A description for testing.",
            context="Test context"
        )
        
        # Verify the result
        assert result["definition"] == "A test concept definition."
        assert result["key_attributes"] == ["attr1", "attr2"]
        
        # Verify the AI client was called with correct parameters
        mock_chat.assert_called_once()
        call_args = mock_chat.call_args
        assert call_args.kwargs.get("response_format") == {"type": "json_object"}
        
        # Check prompt content in messages
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        assert len(messages) == 2
        assert "Test Concept" in messages[1]["content"]
        assert "A description for testing." in messages[1]["content"]

