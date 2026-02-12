import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class ErrorRecord(Base):
    __tablename__ = "error_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    error_type: Mapped[str] = mapped_column(String(50), nullable=False) # network/ai_service/database/validation/unknown
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    source_service: Mapped[str] = mapped_column(String(50), nullable=False)
    source_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=0)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ErrorRecord(id={self.id}, type={self.error_type}, resolved={self.is_resolved})>"
