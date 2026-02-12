import uuid
import enum
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class HotspotStatus(str, enum.Enum):
    EMERGING = "emerging"
    TRENDING = "trending"
    MATURE = "mature"
    COOLING = "cooling"
    ARCHIVED = "archived"

class Hotspot(Base):
    __tablename__ = "hotspots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[HotspotStatus] = mapped_column(Enum(HotspotStatus), default=HotspotStatus.EMERGING, nullable=False)
    
    mention_count: Mapped[int] = mapped_column(Integer, default=0)
    recent_7d_count: Mapped[int] = mapped_column(Integer, default=0)
    previous_7d_count: Mapped[int] = mapped_column(Integer, default=0)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    display_priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Storing lists of IDs as JSON
    related_node_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    related_content_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_mentioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    events: Mapped[List["HotspotEvent"]] = relationship("HotspotEvent", back_populates="hotspot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hotspot(id={self.id}, topic={self.topic_name}, status={self.status})>"
