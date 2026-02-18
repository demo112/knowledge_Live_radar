import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_test_service import AITestService

@pytest.mark.asyncio
async def test_test_connection_success():
    """Test successful connection"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.api_key": return "test_key"
            if key == "ai.base_url": return "https://api.test"
            if key == "ai.model": return "test-model"
            if key == "ai.timeout": return 60.0
            return None
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            service = AITestService()
            result = await service.test_connection()
            
            assert result["success"] is True
            assert "连接测试成功" in result["message"]
            assert "latency_ms" in result
            assert result["model"] == "test-model"
            
            mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_test_connection_disabled():
    """Test disabled state"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return False
            if key == "ai.timeout": return 60.0
            if key == "ai.local.timeout": return 30.0
            return "val"
        mock_config.get.side_effect = get_side_effect
        
        service = AITestService()
        result = await service.test_connection()
        
        assert result["success"] is False
        assert result["code"] == "AI_DISABLED"

@pytest.mark.asyncio
async def test_test_connection_missing_key():
    """Test missing API key"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.api_key": return ""
            if key == "ai.timeout": return 60.0
            if key == "ai.local.timeout": return 30.0
            return "val"
        mock_config.get.side_effect = get_side_effect
        
        service = AITestService()
        result = await service.test_connection()
        
        assert result["success"] is False
        assert result["code"] == "API_KEY_MISSING"

@pytest.mark.asyncio
async def test_test_connection_failure():
    """Test connection failure (e.g. timeout or API error)"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        def get_side_effect(key):
            if key == "ai.enabled": return True
            if key == "ai.timeout": return 60.0
            if key == "ai.local.timeout": return 30.0
            return "val"
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            # Simulate exception
            mock_client.chat.completions.create.side_effect = Exception("Timeout")
            
            service = AITestService()
            result = await service.test_connection()
            
            assert result["success"] is False
            assert result["code"] == "CONNECTION_FAILED"
            assert "Timeout" in result["message"]

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
