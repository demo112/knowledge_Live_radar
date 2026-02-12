import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum

class BatchTaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"

class BatchTask(Base):
    __tablename__ = "batch_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False) # file_upload, url_import
    status: Mapped[BatchTaskStatus] = mapped_column(SQLEnum(BatchTaskStatus), default=BatchTaskStatus.PENDING)
    
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)
    
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Summary or list of created IDs
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BatchTask(id={self.id}, type={self.task_type}, status={self.status})>"
