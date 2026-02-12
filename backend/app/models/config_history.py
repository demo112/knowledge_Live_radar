import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class ConfigHistory(Base):
    __tablename__ = "config_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    config_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Store values as JSON string or JSON type? Requirement says "value".
    # Since config values can be anything, JSON is good.
    # But if they are primitives, storing as string representation might be safer if JSON is overkill?
    # I'll use JSON to support structured config.
    old_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    
    changed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # user id or system
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ConfigHistory(id={self.id}, key={self.config_key})>"
