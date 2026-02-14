from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.services.config.configuration_service import configuration_service
from app.services.ai_test_service import AITestService
from app.models.config_history import ConfigHistory

class ConfigHistoryRead(BaseModel):
    id: UUID
    config_key: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    changed_by: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConfigUpdate(BaseModel):
    value: Any

router = APIRouter(
    prefix="/config",
    tags=["config"]
)

@router.get("/", response_model=Dict[str, Any])
async def get_all_configs():
    """
    Get all current configuration values with sensitive data masked.
    """
    configs = configuration_service.get_all()
    # Mask sensitive keys
    if "ai.api_key" in configs:
        configs["ai.api_key"] = configuration_service.get_masked("ai.api_key")
    return configs

@router.get("/history", response_model=List[ConfigHistoryRead])
async def get_config_history(
    key: Optional[str] = None,
    limit: int = 50
):
    """
    Get configuration change history.
    """
    history = await configuration_service.get_history(key, limit)
    return history

@router.get("/{key}")
async def get_config(key: str):
    """
    Get a specific configuration value.
    """
    value = configuration_service.get_masked(key)
    if value is None and key not in configuration_service.get_all():
        raise HTTPException(status_code=404, detail="配置项未找到")
    return {"key": key, "value": value}

@router.put("/{key}")
async def update_config(
    key: str,
    update: ConfigUpdate
):
    """
    Update a configuration value.
    """
    try:
        await configuration_service.set(key, update.value, user_id="admin") # TODO: Get user from auth
        # Return masked value if sensitive
        new_value = update.value
        if key == "ai.api_key":
            new_value = configuration_service.get_masked(key)
            
        return {"status": "success", "key": key, "value": new_value}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/test")
async def test_ai_connection(target: str = "auto"):
    """
    Test connectivity to the AI provider using current configuration.
    target: "auto", "local", "cloud"
    """
    service = AITestService()
    return await service.test_connection(target)
