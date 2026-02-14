import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_ai_fallback_local_failure():
    # Mock configuration
    with patch("app.services.ai_service.configuration_service") as mock_config:
        # Setup config defaults
        def get_config_side_effect(key, default=None):
            config = {
                "ai.enabled": True,
                "ai.api_key": "sk-cloud",
                "ai.base_url": "https://cloud.api",
                "ai.local.enabled": True,
                "ai.local.base_url": "http://local.api",
                "ai.local.timeout": 1.0,
                "ai.strategy": "local_first",
                "ai.model": "cloud-model",
                "ai.local.model": "local-model",
                "ai.temperature": 0.7,
                "ai.max_retries": 1
            }
            return config.get(key, default)
        
        mock_config.get.side_effect = get_config_side_effect
        
        # Instantiate service
        service = AIService()
        
        # Mock clients
        mock_local_client = AsyncMock()
        mock_cloud_client = AsyncMock()
        
        # Inject mocks
        service._local_client = mock_local_client
        service._cloud_client = mock_cloud_client
        
        # Scenario: Local fails, Cloud succeeds
        mock_local_client.chat.completions.create.side_effect = Exception("Connection refused")
        
        mock_cloud_response = MagicMock()
        mock_cloud_response.choices = [MagicMock(message=MagicMock(content="Cloud Response"))]
        mock_cloud_client.chat.completions.create.return_value = mock_cloud_response
        
        # Execute
        result = await service.chat_completion([{"role": "user", "content": "hi"}])
        
        # Assertions
        assert result == "Cloud Response"
        
        # Verify Local was called
        mock_local_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_local_client.chat.completions.create.call_args
        assert kwargs['model'] == "local-model"
        
        # Verify Cloud was called
        mock_cloud_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_cloud_client.chat.completions.create.call_args
        assert kwargs['model'] == "cloud-model"

@pytest.mark.asyncio
async def test_ai_local_success():
    # Mock configuration
    with patch("app.services.ai_service.configuration_service") as mock_config:
        def get_config_side_effect(key, default=None):
            config = {
                "ai.enabled": True,
                "ai.api_key": "sk-cloud",
                "ai.base_url": "https://cloud.api",
                "ai.local.enabled": True,
                "ai.local.base_url": "http://local.api",
                "ai.local.timeout": 1.0,
                "ai.strategy": "local_first",
                "ai.model": "cloud-model",
                "ai.local.model": "local-model"
            }
            return config.get(key, default)
        mock_config.get.side_effect = get_config_side_effect
        
        service = AIService()
        mock_local_client = AsyncMock()
        mock_cloud_client = AsyncMock()
        service._local_client = mock_local_client
        service._cloud_client = mock_cloud_client
        
        # Scenario: Local succeeds
        mock_local_response = MagicMock()
        mock_local_response.choices = [MagicMock(message=MagicMock(content="Local Response"))]
        mock_local_client.chat.completions.create.return_value = mock_local_response
        
        result = await service.chat_completion([{"role": "user", "content": "hi"}])
        
        assert result == "Local Response"
        mock_local_client.chat.completions.create.assert_called_once()
        mock_cloud_client.chat.completions.create.assert_not_called()
