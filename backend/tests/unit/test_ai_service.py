import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_chat_completion_success():
    # Mock settings to ensure API key is present
    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.SILICONFLOW_API_KEY = "test_key"
        mock_settings.SILICONFLOW_BASE_URL = "https://api.test"
        
        # Initialize service with mocked settings
        service = AIService()
        
        # Mock the client
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        service.client = AsyncMock()
        service.client.chat.completions.create.return_value = mock_response
        
        response = await service.chat_completion([{"role": "user", "content": "Hello"}])
        
        assert response == "Test response"
        service.client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completion_no_client():
    # Mock settings to simulate missing API key
    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.SILICONFLOW_API_KEY = None
        
        service = AIService()
        
        # Since client is None, it should return None and log error
        response = await service.chat_completion([{"role": "user", "content": "Hello"}])
        
        assert response is None
