import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., "create_node", "update_node"
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True) # Target entity ID if exists
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True) # pending, approved, rejected
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Payload for the change
    
    # New fields for Iteration 3
    source_content_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("content_items.id"), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(50), default="user", server_default="user") # user, ai
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Proposal reason
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # AI confidence
    original_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Snapshot for rollback
    impact_analysis: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Impact analysis result

    applicant_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # User ID or "system"
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    review_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    source_content: Mapped[Optional["app.models.content.ContentItem"]] = relationship("app.models.content.ContentItem")

    def __repr__(self):
        return f"<Approval(id={self.id}, type={self.type}, status={self.status})>"
