import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_chat_completion_success():
    # Mock configuration_service
    with patch("app.services.ai_service.configuration_service") as mock_config:
        def get_side_effect(key, default=None):
            if key == "ai.enabled": return True
            if key == "ai.api_key": return "test_key"
            if key == "ai.base_url": return "https://api.test"
            if key == "ai.max_retries": return 3
            if key == "ai.model": return "test-model"
            if key == "ai.temperature": return 0.7
            if key == "ai.timeout": return 60.0
            if key == "ai.local.enabled": return False
            if key == "ai.local.timeout": return 5.0
            return default
        mock_config.get.side_effect = get_side_effect
        
        # Initialize service
        with patch("app.services.ai_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = AsyncMock()
            mock_openai_cls.return_value = mock_client_instance
            
            service = AIService()
            
            # Setup mock response
            mock_response = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "Test response"
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            
            mock_client_instance.chat.completions.create.return_value = mock_response
            
            response = await service.chat_completion([{"role": "user", "content": "Hello"}])
            
            assert response == "Test response"
            mock_client_instance.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completion_no_client():
    # Mock configuration to simulate disabled
    with patch("app.services.ai_service.configuration_service") as mock_config:
        def get_side_effect(key, default=None):
            if key == "ai.enabled": return False
            if key == "ai.local.enabled": return False
            return default
        mock_config.get.side_effect = get_side_effect
        
        service = AIService()
        
        # Since client is None, it should return None
        response = await service.chat_completion([{"role": "user", "content": "Hello"}])
        
        assert response is None
