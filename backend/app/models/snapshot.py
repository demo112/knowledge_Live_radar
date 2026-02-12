import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pyramid_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramids.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "v1.0.0" or timestamp based
    data: Mapped[dict] = mapped_column(JSON, nullable=False) # Full pyramid state
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Why this snapshot was taken
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pyramid: Mapped["app.models.pyramid.Pyramid"] = relationship("app.models.pyramid.Pyramid")

    def __repr__(self):
        return f"<Snapshot(id={self.id}, version={self.version})>"
