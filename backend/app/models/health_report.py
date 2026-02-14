import uuid
import enum
from datetime import datetime
from typing import Optional, Any, Dict, List

from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class HealthReportType(str, enum.Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    TRIGGERED = "triggered"
    EVOLUTION_CYCLE = "evolution_cycle"

class HealthReport(Base):
    __tablename__ = "health_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    report_type: Mapped[HealthReportType] = mapped_column(Enum(HealthReportType), default=HealthReportType.SCHEDULED)
    
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # JSON fields for detailed metrics
    pyramid_scores: Mapped[Dict[str, float]] = mapped_column(JSON, default={})
    source_health_score: Mapped[float] = mapped_column(Float, default=0.0)
    content_coverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    hotspot_distribution: Mapped[Dict[str, int]] = mapped_column(JSON, default={})
    approval_backlog: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    crawl_stats: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    
    issues: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=[])
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<HealthReport(id={self.id}, score={self.overall_score}, type={self.report_type})>"
