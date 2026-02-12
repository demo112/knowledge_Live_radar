import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "crawl", "health_check"
    
    cron_expression: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=60)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    executions: Mapped[List["TaskExecution"]] = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScheduledTask(id={self.id}, name={self.task_name}, active={self.is_active})>"
