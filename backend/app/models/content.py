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
    concepts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True) # AI extracted concepts
    
    submitter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # User ID who submitted this
    input_type: Mapped[str] = mapped_column(String(20), default="url", server_default="url") # url, pdf, word, markdown, image, text
    ai_processed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    ai_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True) # AI analysis metadata (reasoning, confidence, etc.)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    
    # Metabolism fields
    lifecycle_status: Mapped[str] = mapped_column(String(20), default="ACTIVE", server_default="ACTIVE", index=True) # ACTIVE, DEPRECATED, ARCHIVED, DELETED
    metabolism_score: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0", index=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    source: Mapped[Optional["InformationSource"]] = relationship("app.models.source.InformationSource")
    validation_result: Mapped[Optional["ValidationResult"]] = relationship("ValidationResult", uselist=False, back_populates="content")
    node_relations: Mapped[List["ContentNodeRelation"]] = relationship("ContentNodeRelation", back_populates="content", cascade="all, delete-orphan")
    
    @property
    def nodes(self) -> List["ContentNodeRelation"]:
        return self.node_relations

    def __repr__(self):
        return f"<ContentItem(id={self.id}, title={self.title})>"


class ContentNodeRelation(Base):
    __tablename__ = "content_node_relations"

    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id", ondelete="CASCADE"), primary_key=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, server_default="1.0")
    source: Mapped[str] = mapped_column(String(20), default="manual", server_default="manual") # manual, ai_auto, ai_confirm
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_manual: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true") # Deprecated, use source instead

    # Relationships
    content: Mapped["ContentItem"] = relationship("ContentItem", back_populates="node_relations")
    node: Mapped["PyramidNode"] = relationship("app.models.pyramid.PyramidNode")

    @property
    def id(self) -> uuid.UUID:
        return self.node_id

    @property
    def name(self) -> str:
        return self.node.name if self.node else ""

    @property
    def pyramid_id(self) -> uuid.UUID:
        return self.node.pyramid_id if self.node else None

    @property
    def pyramid_name(self) -> str:
        return self.node.pyramid.name if self.node and self.node.pyramid else ""

    def __repr__(self):
        return f"<ContentNodeRelation(content_id={self.content_id}, node_id={self.node_id}, source={self.source})>"


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
