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
            return None
        mock_config.get.side_effect = get_side_effect
        
        with patch("app.services.ai_test_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            service = AITestService()
            result = await service.test_connection()
            
            assert result["success"] is True
            assert result["message"] == "连接测试成功"
            assert "latency_ms" in result
            assert result["model"] == "test-model"
            
            mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_test_connection_disabled():
    """Test disabled state"""
    with patch("app.services.ai_test_service.configuration_service") as mock_config:
        mock_config.get.side_effect = lambda k: False if k == "ai.enabled" else "val"
        
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
        mock_config.get.side_effect = lambda k: True if k == "ai.enabled" else "val"
        
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
