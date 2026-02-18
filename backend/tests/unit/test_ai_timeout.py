
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_test_service import AITestService

@pytest.mark.asyncio
async def test_test_connection_uses_configured_timeout_local():
    """Test that local connection uses configured timeout"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.local.base_url": return "http://localhost:11434/v1"
            if key == "ai.local.model": return "qwen2.5:7b"
            if key == "ai.local.timeout": return 45.0  # Configured timeout
            if key == "ai.strategy": return "local_first"
            return None
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            service = AITestService()
            await service.test_connection(target="local")
            
            # Verify AsyncOpenAI was called with timeout=45.0
            mock_openai.assert_called_with(
                api_key="ollama",
                base_url="http://localhost:11434/v1",
                timeout=45.0,
                max_retries=0
            )

@pytest.mark.asyncio
async def test_test_connection_uses_configured_timeout_cloud():
    """Test that cloud connection uses configured timeout"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.api_key": return "sk-test"
            if key == "ai.base_url": return "https://api.test"
            if key == "ai.model": return "gpt-4"
            if key == "ai.timeout": return 90.0  # Configured timeout
            if key == "ai.strategy": return "cloud_only"
            return None
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            service = AITestService()
            await service.test_connection(target="cloud")
            
            # Verify AsyncOpenAI was called with timeout=90.0
            mock_openai.assert_called_with(
                api_key="sk-test",
                base_url="https://api.test",
                timeout=90.0,
                max_retries=0
            )

@pytest.mark.asyncio
async def test_test_connection_uses_default_timeout_if_missing():
    """Test default timeout if config is missing"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.local.base_url": return "http://localhost:11434/v1"
            if key == "ai.local.model": return "qwen2.5:7b"
            if key == "ai.local.timeout": return None  # Missing config
            if key == "ai.strategy": return "local_first"
            return None
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            service = AITestService()
            await service.test_connection(target="local")
            
            # Verify AsyncOpenAI was called with default timeout (30.0 for local)
            mock_openai.assert_called_with(
                api_key="ollama",
                base_url="http://localhost:11434/v1",
                timeout=30.0,
                max_retries=0
            )
