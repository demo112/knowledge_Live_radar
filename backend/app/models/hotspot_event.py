import uuid
import enum
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class HotspotEventType(str, enum.Enum):
    STATUS_CHANGE = "status_change"
    PRIORITY_CHANGE = "priority_change"
    MANUAL_UPDATE = "manual_update"
    SYSTEM_UPDATE = "system_update"

class HotspotEvent(Base):
    __tablename__ = "hotspot_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    hotspot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hotspots.id"), nullable=False)
    
    event_type: Mapped[HotspotEventType] = mapped_column(Enum(HotspotEventType), nullable=False)
    
    # Store status as string to avoid tight coupling if status enum changes, 
    # or import HotspotStatus. Using string is safer for history.
    old_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    trigger_condition: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    operator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Who triggered it (system or user_id)
    
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Extra details
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hotspot: Mapped["Hotspot"] = relationship("Hotspot", back_populates="events")

    def __repr__(self):
        return f"<HotspotEvent(id={self.id}, type={self.event_type}, hotspot={self.hotspot_id})>"
