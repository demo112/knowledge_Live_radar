import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.models.approval import Approval

logger = logging.getLogger(__name__)

# Level priority for filtering
LEVEL_PRIORITY = {"info": 0, "warning": 1, "critical": 2}


class NotificationService:

    async def _get_preferences(self, db: AsyncSession) -> Optional[NotificationPreference]:
        result = await db.execute(select(NotificationPreference).limit(1))
        return result.scalar_one_or_none()

    async def _should_send(self, level: str, prefs: Optional[NotificationPreference]) -> bool:
        """Check quiet hours and level filter."""
        if not prefs:
            return True  # No preferences configured, send everything

        # Level filter
        min_level = prefs.min_level or "info"
        if LEVEL_PRIORITY.get(level, 0) < LEVEL_PRIORITY.get(min_level, 0):
            return False

        # Quiet hours
        if prefs.quiet_hours_enabled:
            now = datetime.now(timezone.utc)
            current_time = now.strftime("%H:%M")
            start = prefs.quiet_hours_start or "22:00"
            end = prefs.quiet_hours_end or "08:00"

            in_quiet = (
                (start <= current_time or current_time < end)
                if start > end
                else (start <= current_time < end)
            )
            if in_quiet:
                if level == "critical" and prefs.quiet_hours_allow_critical:
                    return True
                return False

        return True

    async def send(
        self,
        title: str,
        message: str,
        level: str = "info",
        source_type: str = "system",
        source_id: Optional[str] = None,
    ):
        """
        Create a notification record in the database.
        Respects quiet hours and level filters.
        """
        async with AsyncSessionLocal() as db:
            try:
                prefs = await self._get_preferences(db)

                if not await self._should_send(level, prefs):
                    logger.debug(f"Notification suppressed (level={level}): {title}")
                    return

                channels_sent = ["in_app"]

                notification = Notification(
                    level=level,
                    title=title,
                    message=message,
                    source_type=source_type,
                    source_id=source_id,
                    channels_sent=channels_sent,
                )
                db.add(notification)
                await db.commit()

                logger.info(f"[NOTIFICATION][{level.upper()}] {title}")

            except Exception as e:
                logger.error(f"Failed to create notification: {e}")
                await db.rollback()

    # ── Convenience methods ──────────────────────────────────────

    async def notify_approval_status_change(
        self, approval: Approval, old_status: str, new_status: str
    ):
        title = f"Approval status: {old_status} → {new_status}"
        message = (
            f"Approval {approval.id} ({approval.type}) "
            f"changed from {old_status} to {new_status}."
        )
        level = "info" if new_status == "executed" else "warning"
        await self.send(
            title=title,
            message=message,
            level=level,
            source_type="proposal",
            source_id=str(approval.id),
        )

    async def notify_new_proposal(self, approval: Approval):
        await self.send(
            title=f"New proposal: {approval.type}",
            message=f"AI generated a new {approval.type} proposal. Reason: {approval.reason or 'N/A'}",
            level="info",
            source_type="proposal",
            source_id=str(approval.id),
        )

    async def notify_source_health_alert(
        self, source_name: str, source_id: str, error_count: int
    ):
        level = "critical" if error_count > 5 else "warning"
        await self.send(
            title=f"Source health alert: {source_name}",
            message=f"Source '{source_name}' has failed {error_count} times consecutively.",
            level=level,
            source_type="source_health",
            source_id=source_id,
        )

    async def notify_system_health(self, overall_score: float, issues_count: int):
        level = "critical" if overall_score < 50 else ("warning" if overall_score < 70 else "info")
        await self.send(
            title=f"System health: {overall_score:.0f}/100",
            message=f"System health score is {overall_score:.0f}. {issues_count} issues detected.",
            level=level,
            source_type="system_health",
        )

    async def notify_ai_service_failure(self, error: str):
        await self.send(
            title="AI service unavailable",
            message=f"AI service call failed after retries: {error}",
            level="critical",
            source_type="ai_service",
        )

    async def notify_suggestion_status_change(
        self, suggestion, old_status: str, new_status: str
    ):
        action_type_display = {
            "create_node": "创建节点",
            "delete_node": "删除节点",
            "update_node": "更新节点",
            "split_node": "拆分节点",
            "merge_node": "合并节点",
            "link_content": "关联内容",
            "update_strategy": "更新策略",
            "archive_content": "归档内容",
        }.get(suggestion.action_type, suggestion.action_type)

        status_display = {
            "pending": "待审批",
            "approved": "已审批",
            "rejected": "已拒绝",
            "executed": "已执行",
        }

        title = f"AI建议状态变更: {status_display.get(old_status, old_status)} → {status_display.get(new_status, new_status)}"
        message = (
            f"AI建议 ({action_type_display}) "
            f"状态从 {status_display.get(old_status, old_status)} 变更为 {status_display.get(new_status, new_status)}。"
            f"原因: {suggestion.reason or '无'}"
        )
        level = "info" if new_status == "executed" else "warning"
        await self.send(
            title=title,
            message=message,
            level=level,
            source_type="ai_suggestion",
            source_id=str(suggestion.id),
        )


notification_service = NotificationService()
