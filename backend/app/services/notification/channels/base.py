import logging
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: Any, message: Dict[str, Any]) -> bool:
        pass

class InAppChannel(NotificationChannel):
    async def send(self, recipient: Any, message: Dict[str, Any]) -> bool:
        # In-app notifications are stored in DB, so "sending" is just a no-op here
        # or handled by the service persisting the notification.
        return True

class WebhookChannel(NotificationChannel):
    async def send(self, recipient: str, message: Dict[str, Any]) -> bool:
        if not recipient:
            return False
        try:
            async with httpx.AsyncClient() as client:
                await client.post(recipient, json=message, timeout=5.0)
            return True
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False
