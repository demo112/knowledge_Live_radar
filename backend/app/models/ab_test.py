import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class ABTest(Base):
    __tablename__ = "ab_tests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_templates.id"), nullable=False)
    version_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_versions.id"), nullable=False)
    version_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_versions.id"), nullable=False)
    traffic_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.5) # Ratio for Version A (0.0 to 1.0)
    
    status: Mapped[str] = mapped_column(String(20), default="running") # running, completed, cancelled
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Results
    version_a_calls: Mapped[int] = mapped_column(Integer, default=0)
    version_b_calls: Mapped[int] = mapped_column(Integer, default=0)
    version_a_avg_quality: Mapped[float] = mapped_column(Float, default=0.0)
    version_b_avg_quality: Mapped[float] = mapped_column(Float, default=0.0)
    winner_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("prompt_versions.id"), nullable=True)
    
    # Relationships
    template: Mapped["PromptTemplate"] = relationship("PromptTemplate", back_populates="ab_tests")
    version_a: Mapped["PromptVersion"] = relationship("PromptVersion", foreign_keys=[version_a_id])
    version_b: Mapped["PromptVersion"] = relationship("PromptVersion", foreign_keys=[version_b_id])
    winner_version: Mapped[Optional["PromptVersion"]] = relationship("PromptVersion", foreign_keys=[winner_version_id])

    def __repr__(self):
        return f"<ABTest(id={self.id}, template_id={self.template_id}, status={self.status})>"
