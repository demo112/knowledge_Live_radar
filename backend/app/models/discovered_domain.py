import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class DiscoveredDomain(Base):
    __tablename__ = "discovered_domains"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    evaluation_status: Mapped[str] = mapped_column(String(20), default="PENDING") # PENDING, APPROVED, REJECTED, IGNORED
    has_rss: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Optional link to a change proposal if one was generated
    proposal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("approvals.id"), nullable=True)

    def __repr__(self):
        return f"<DiscoveredDomain(id={self.id}, domain={self.domain}, count={self.occurrence_count})>"
