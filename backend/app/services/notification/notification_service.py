import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.services.notification.channels import InAppChannel, WebhookChannel

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.in_app_channel = InAppChannel()
        self.webhook_channel = WebhookChannel()
        
    async def send(self, level: str, title: str, message: str, source_type: str, source_id: Optional[str] = None):
        async with AsyncSessionLocal() as session:
            # Get preferences (Assuming single global preference or per user. Here assuming single/system wide)
            stmt = select(NotificationPreference).limit(1)
            pref = await session.scalar(stmt)
            
            if not pref:
                # Create default if not exists
                pref = NotificationPreference()
                session.add(pref)
                await session.commit()
                await session.refresh(pref)
                
            # Check level
            levels = {"info": 0, "warning": 1, "critical": 2}
            if levels.get(level, 0) < levels.get(pref.min_level, 0):
                return
                
            # Check quiet hours
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            is_quiet = False
            if pref.quiet_hours_enabled:
                if pref.quiet_hours_start <= current_time_str or current_time_str < pref.quiet_hours_end: # Simple cross-midnight check needs logic
                    # If start > end (e.g. 22:00 to 08:00), then quiet if time >= start OR time < end
                    if pref.quiet_hours_start > pref.quiet_hours_end:
                        if current_time_str >= pref.quiet_hours_start or current_time_str < pref.quiet_hours_end:
                            is_quiet = True
                    else:
                        if pref.quiet_hours_start <= current_time_str < pref.quiet_hours_end:
                            is_quiet = True
            
            if is_quiet and level != "critical": # Allow critical?
                if not pref.quiet_hours_allow_critical:
                     return # Block critical too if configured
                # If level is critical and allowed, proceed. Else return.
                if level != "critical":
                    return

            channels_sent = []
            webhook_status = None
            
            # In-App (Always save to DB if enabled)
            if pref.in_app_enabled:
                # We save to DB below
                channels_sent.append("in_app")
                
            # Webhook
            if pref.webhook_enabled and pref.webhook_url:
                if not is_quiet or level == "critical": # Webhook might wake people up
                    success = await self.webhook_channel.send(pref.webhook_url, {
                        "level": level,
                        "title": title,
                        "message": message,
                        "source": source_type,
                        "timestamp": now.isoformat()
                    })
                    if success:
                        channels_sent.append("webhook")
                        webhook_status = "success"
                    else:
                        webhook_status = "failed"
            
            # Persist
            notification = Notification(
                level=level,
                title=title,
                message=message,
                source_type=source_type,
                source_id=source_id,
                channels_sent=channels_sent,
                webhook_status=webhook_status
            )
            session.add(notification)
            await session.commit()

    async def list_notifications(self, page: int = 1, size: int = 20) -> List[Notification]:
        async with AsyncSessionLocal() as session:
            stmt = select(Notification).order_by(Notification.created_at.desc()).offset((page - 1) * size).limit(size)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_unread_count(self) -> int:
        async with AsyncSessionLocal() as session:
            stmt = select(func.count()).where(Notification.is_read == False)
            return await session.scalar(stmt) or 0

    async def mark_read(self, notification_id: str):
        async with AsyncSessionLocal() as session:
            notif = await session.get(Notification, notification_id)
            if notif:
                notif.is_read = True
                notif.read_at = datetime.now()
                await session.commit()

notification_service = NotificationService()
