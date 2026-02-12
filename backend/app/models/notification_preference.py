import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Channel Config
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    webhook_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    webhook_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Level Filter
    min_level: Mapped[str] = mapped_column(String(20), default="info") # info/warning/critical
    
    # Quiet Hours
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    quiet_hours_start: Mapped[str] = mapped_column(String(5), default="22:00")
    quiet_hours_end: Mapped[str] = mapped_column(String(5), default="08:00")
    quiet_hours_allow_critical: Mapped[bool] = mapped_column(Boolean, default=True)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<NotificationPreference(id={self.id})>"
