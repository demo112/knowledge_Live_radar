import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("information_sources.id"), nullable=True)
    original_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publish_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True) # Using JSON for SQLite compatibility
    
    submitter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # User ID who submitted this
    input_type: Mapped[str] = mapped_column(String(20), default="url", server_default="url") # url, pdf, word, markdown, image, text
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    source: Mapped[Optional["InformationSource"]] = relationship("app.models.source.InformationSource")
    validation_result: Mapped[Optional["ValidationResult"]] = relationship("ValidationResult", uselist=False, back_populates="content")
    
    def __repr__(self):
        return f"<ContentItem(id={self.id}, title={self.title})>"


class ContentNodeRelation(Base):
    __tablename__ = "content_node_relations"

    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id"), primary_key=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    content: Mapped["ContentItem"] = relationship("ContentItem")
    node: Mapped["PyramidNode"] = relationship("app.models.pyramid.PyramidNode")

    def __repr__(self):
        return f"<ContentNodeRelation(content_id={self.content_id}, node_id={self.node_id})>"


class ValidationResult(Base):
    __tablename__ = "validation_results"

    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"), primary_key=True)
    hard_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    soft_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    cross_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    overall_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    content: Mapped["ContentItem"] = relationship("ContentItem", back_populates="validation_result")

    def __repr__(self):
        return f"<ValidationResult(content_id={self.content_id}, score={self.overall_score})>"
