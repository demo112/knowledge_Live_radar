import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.ai.processors.suggestion import SuggestionProcessor

@pytest.fixture
def processor():
    return SuggestionProcessor()

@pytest.mark.asyncio
async def test_parse_suggestions_valid_json(processor):
    response_text = """
    {
        "analysis": {"score": 80},
        "suggestions": [
            {
                "action_type": "create_node",
                "target_name": "New Node",
                "reason": "Test reason",
                "params": {"name": "New Node"}
            }
        ]
    }
    """
    
    with patch("app.core.ai.client.ai_client.parse_json") as mock_parse:
        mock_parse.return_value = {
            "analysis": {"score": 80},
            "suggestions": [
                {
                    "action_type": "create_node",
                    "target_name": "New Node",
                    "reason": "Test reason",
                    "params": {"name": "New Node"}
                }
            ]
        }
        
        result = processor._parse_suggestions(response_text)
        assert len(result) == 1
        assert result[0]["action_type"] == "create_node"
