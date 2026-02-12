import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class InformationSource(Base):
    __tablename__ = "information_sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False) # RSS, API, WEB, USER
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    config: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="DISCOVERED")
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_interval: Mapped[int] = mapped_column(Integer, default=3600)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # node_relations = relationship("SourceNodeRelation", back_populates="source")
    # contents = relationship("ContentItem", back_populates="source")
    crawl_jobs: Mapped[List["CrawlJob"]] = relationship("app.models.crawl_job.CrawlJob", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InformationSource(id={self.id}, name={self.name}, type={self.type})>"


class SourceNodeRelation(Base):
    __tablename__ = "source_node_relations"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("information_sources.id"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Relationships
    source: Mapped["InformationSource"] = relationship("InformationSource")
    node: Mapped["PyramidNode"] = relationship("app.models.pyramid.PyramidNode")

    def __repr__(self):
        return f"<SourceNodeRelation(source_id={self.source_id}, node_id={self.node_id})>"
