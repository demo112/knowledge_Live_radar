import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    level: Mapped[str] = mapped_column(String(20), nullable=False) # info/warning/critical
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # proposal/source_health/system_health/ai_service/task
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # ID as string to be generic
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Sent Channels
    channels_sent: Mapped[List[str]] = mapped_column(JSON, default=list) # ["in_app", "webhook"]
    webhook_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # success/failed/skipped
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title}, level={self.level})>"
