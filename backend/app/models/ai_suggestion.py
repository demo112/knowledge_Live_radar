import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), index=True)

    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="create_node",
        comment="操作类型: create_node/delete_node/update_node/split_node/merge_node/link_content/update_strategy/archive_content",
    )

    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="pyramid_node",
        comment="目标实体类型: pyramid_node/information_source/content_item",
    )
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True, comment="目标实体 ID")
    target_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="目标名称（便于用户识别）")

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="",
        comment="AI 生成的原因（人类可读）",
    )
    params: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        server_default="{}",
        comment="执行参数（AI 可执行）",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        index=True,
        comment="状态: pending/approved/executed/rejected",
    )

    pyramid_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("pyramids.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的金字塔",
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("information_sources.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的信息源",
    )

    def __repr__(self):
        return f"<AISuggestion(id={self.id}, type={self.type}, action_type={self.action_type}, status={self.status})>"
