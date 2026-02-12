import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class TaskExecution(Base):
    __tablename__ = "task_executions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scheduled_tasks.id"), nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, running, success, failed
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    task: Mapped["ScheduledTask"] = relationship("ScheduledTask", back_populates="executions")

    def __repr__(self):
        return f"<TaskExecution(id={self.id}, task={self.task_id}, status={self.status})>"
