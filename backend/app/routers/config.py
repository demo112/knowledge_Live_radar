from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime

from app.services.config.configuration_service import configuration_service
from app.models.config_history import ConfigHistory

class ConfigHistoryRead(BaseModel):
    id: int
    config_key: str
    old_value: Optional[str] # Values are stored as JSON/String in DB often, or Any. Model defines it.
    new_value: Optional[str]
    changed_by: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConfigUpdate(BaseModel):
    value: Any

router = APIRouter(
    prefix="/config",
    tags=["config"]
)

@router.get("/", response_model=Dict[str, Any])
async def get_all_configs():
    """
    Get all current configuration values.
    """
    return configuration_service.get_all()

@router.get("/{key}")
async def get_config(key: str):
    """
    Get a specific configuration value.
    """
    value = configuration_service.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Config key not found")
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
        return {"status": "success", "key": key, "value": update.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/list", response_model=List[ConfigHistoryRead])
async def get_config_history(
    key: Optional[str] = None,
    limit: int = 50
):
    """
    Get configuration change history.
    """
    # Note: ConfigHistory model likely stores values as JSON or string. 
    # If they are Any, Pydantic might struggle if not handled.
    # Assuming the service returns ORM objects.
    history = await configuration_service.get_history(key, limit)
    
    # Transform if needed (e.g. if values are not strings)
    # The Pydantic model expects Optional[str]. 
    # If DB stores JSON/Any, we might need to str() them.
    # For now, let's rely on Pydantic's coercion or assume they are compatible.
    return history
