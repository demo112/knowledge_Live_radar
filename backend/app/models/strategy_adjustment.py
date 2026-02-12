import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class StrategyAdjustment(Base):
    __tablename__ = "strategy_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("information_sources.id"), nullable=True)
    
    adjustment_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. frequency, timeout, retry_limit
    
    old_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    proposal_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True) # Link to ChangeProposal
    
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source: Mapped[Optional["InformationSource"]] = relationship("app.models.source.InformationSource")

    def __repr__(self):
        return f"<StrategyAdjustment(id={self.id}, type={self.adjustment_type}, source={self.source_id})>"
