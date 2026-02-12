import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scene: Mapped[str] = mapped_column(String(50), nullable=False, unique=True) # quality_eval/summary/etc
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("prompt_versions.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    versions: Mapped[List["PromptVersion"]] = relationship("PromptVersion", back_populates="template", foreign_keys="PromptVersion.template_id", cascade="all, delete-orphan")
    current_version: Mapped[Optional["PromptVersion"]] = relationship("PromptVersion", foreign_keys=[current_version_id], post_update=True)
    ab_tests: Mapped[List["ABTest"]] = relationship("ABTest", back_populates="template")

    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, scene={self.scene}, name={self.name})>"
