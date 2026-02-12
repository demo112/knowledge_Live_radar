from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.notification import notification_service
from app.models.notification_preference import NotificationPreference

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool
    webhook_enabled: bool
    webhook_url: str = None
    min_level: str
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    quiet_hours_allow_critical: bool

@router.get("/")
async def list_notifications(page: int = 1, size: int = 20):
    return await notification_service.list_notifications(page, size)

@router.get("/unread-count")
async def get_unread_count():
    count = await notification_service.get_unread_count()
    return {"count": count}

@router.put("/{id}/read")
async def mark_read(id: str):
    await notification_service.mark_read(id)
    return {"success": True}

# Preference endpoints would require implementing update logic in service
# Skipping for now to focus on core.
