import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class Pyramid(Base):
    __tablename__ = "pyramids"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    
    # Relationships
    nodes: Mapped[List["PyramidNode"]] = relationship("PyramidNode", back_populates="pyramid", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pyramid(id={self.id}, name={self.name})>"


class PyramidNode(Base):
    __tablename__ = "pyramid_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pyramid_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramids.id"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("pyramid_nodes.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    path: Mapped[str] = mapped_column(String(255), index=True) # Materialized path
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, completed
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    
    # Relationships
    pyramid: Mapped["Pyramid"] = relationship("Pyramid", back_populates="nodes")
    parent: Mapped[Optional["PyramidNode"]] = relationship("PyramidNode", remote_side=[id], back_populates="children")
    children: Mapped[List["PyramidNode"]] = relationship("PyramidNode", back_populates="parent", cascade="all, delete-orphan")
    
    # Many-to-Many relationships defined in other modules
    # source_relations = relationship("SourceNodeRelation", back_populates="node")
    # content_relations = relationship("ContentNodeRelation", back_populates="node")

    def __repr__(self):
        return f"<PyramidNode(id={self.id}, name={self.name}, level={self.level})>"
