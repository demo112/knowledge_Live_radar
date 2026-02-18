import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class AIMetric(Base):
    __tablename__ = "ai_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    module: Mapped[str] = mapped_column(String(50), nullable=True, index=True) # e.g., "crawl", "validation", "search"
    model: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., "gpt-4", "deepseek-v3"
    provider: Mapped[str] = mapped_column(String(50), nullable=False) # "cloud" or "local"
    latency: Mapped[float] = mapped_column(Float, nullable=False) # in seconds
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # "success" or "error"
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AIMetric(id={self.id}, model={self.model}, status={self.status})>"
