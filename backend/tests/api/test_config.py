import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
import uuid
from datetime import datetime

@pytest.mark.asyncio
async def test_get_all_configs(client: AsyncClient):
    with patch("app.routers.config.configuration_service") as mock_service:
        mock_service.get_all.return_value = {
            "ai.api_key": "sk-1234567890abcdef",
            "ai.enabled": True,
            "other.key": "value"
        }
        mock_service.get_masked.side_effect = lambda k: "sk-1***cdef" if k == "ai.api_key" else k

        response = await client.get("/api/v1/config/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ai.api_key"] == "sk-1***cdef"
        assert data["ai.enabled"] is True
        assert data["other.key"] == "value"
        
        mock_service.get_masked.assert_any_call("ai.api_key")

@pytest.mark.asyncio
async def test_get_config(client: AsyncClient):
    with patch("app.routers.config.configuration_service") as mock_service:
        # Case 1: Normal key
        mock_service.get_masked.return_value = "value"
        mock_service.get_all.return_value = {"other.key": "value"}
        
        response = await client.get("/api/v1/config/other.key")
        assert response.status_code == 200
        assert response.json() == {"key": "other.key", "value": "value"}
        
        # Case 2: Sensitive key
        mock_service.get_masked.return_value = "sk-1***cdef"
        mock_service.get_all.return_value = {"ai.api_key": "real_key"}
        
        response = await client.get("/api/v1/config/ai.api_key")
        assert response.status_code == 200
        assert response.json() == {"key": "ai.api_key", "value": "sk-1***cdef"}
        
        # Case 3: Not found
        mock_service.get_masked.return_value = None
        mock_service.get_all.return_value = {}
        
        response = await client.get("/api/v1/config/non_existent")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_config(client: AsyncClient):
    with patch("app.routers.config.configuration_service") as mock_service:
        # Case 1: Success
        mock_service.set = AsyncMock()
        
        response = await client.put("/api/v1/config/test.key", json={"value": "new_value"})
        assert response.status_code == 200
        assert response.json() == {"status": "success", "key": "test.key", "value": "new_value"}
        mock_service.set.assert_called_once()
        
        # Case 2: Validation Error (422)
        mock_service.set.side_effect = ValueError("Invalid value")
        
        response = await client.put("/api/v1/config/test.key", json={"value": "bad_value"})
        assert response.status_code == 422
        assert response.json()["detail"] == "Invalid value"

        # Case 3: Sensitive key update return masked
        mock_service.set.side_effect = None
        mock_service.get_masked.return_value = "sk-1***cdef"
        
        response = await client.put("/api/v1/config/ai.api_key", json={"value": "sk-real-key"})
        assert response.status_code == 200
        assert response.json()["value"] == "sk-1***cdef"

@pytest.mark.asyncio
async def test_get_history(client: AsyncClient):
    with patch("app.routers.config.configuration_service") as mock_service:
        history_id = uuid.uuid4()
        now = datetime.now()
        
        mock_history_item = MagicMock()
        mock_history_item.id = history_id
        mock_history_item.config_key = "test.key"
        mock_history_item.old_value = "old"
        mock_history_item.new_value = "new"
        mock_history_item.changed_by = "admin"
        mock_history_item.created_at = now
        
        mock_service.get_history = AsyncMock(return_value=[mock_history_item])
        
        response = await client.get("/api/v1/config/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(history_id)
        assert data[0]["config_key"] == "test.key"

@pytest.mark.asyncio
async def test_ai_connection_endpoint(client: AsyncClient):
    with patch("app.routers.config.AITestService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.test_connection = AsyncMock(return_value={
            "success": True,
            "message": "Connected",
            "latency_ms": 100.0
        })
        
        response = await client.post("/api/v1/config/ai/test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Connected"
        
        mock_instance.test_connection.assert_called_once()
