import logging
from typing import Optional
from app.models.approval import Approval

logger = logging.getLogger(__name__)

class NotificationService:
    async def notify_approval_status_change(self, approval: Approval, old_status: str, new_status: str):
        """
        Notify relevant users about approval status change.
        """
        message = f"Approval {approval.id} status changed from {old_status} to {new_status}"
        logger.info(f"[NOTIFICATION] {message}")
        
        # In a real implementation, this would send an email or WebSocket message
        # to the applicant (approval.applicant_id) or the reviewers.
        
        if approval.applicant_id:
            logger.info(f"[NOTIFICATION] Sending notification to applicant {approval.applicant_id}: {message}")

notification_service = NotificationService()
