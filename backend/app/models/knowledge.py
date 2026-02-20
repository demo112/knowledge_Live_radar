import uuid
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    node_type: Mapped[str] = mapped_column(String(50), default="concept") # concept, technology, tool, method, organization
    
    # AI 认知模型
    ai_model: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 关联 Concept
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("concepts.id"), nullable=True)
    
    # 统计与健康
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    content_count: Mapped[int] = mapped_column(Integer, default=0)
    last_content_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 元数据
    status: Mapped[str] = mapped_column(String(20), default="active") # active, archived
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    outgoing_relations: Mapped[List["KnowledgeNodeRelation"]] = relationship(
        "KnowledgeNodeRelation",
        foreign_keys="[KnowledgeNodeRelation.source_node_id]",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    incoming_relations: Mapped[List["KnowledgeNodeRelation"]] = relationship(
        "KnowledgeNodeRelation",
        foreign_keys="[KnowledgeNodeRelation.target_node_id]",
        back_populates="target_node",
        cascade="all, delete-orphan"
    )
    
    # Many-to-Many via ClusterNodeMembership
    cluster_memberships: Mapped[List["ClusterNodeMembership"]] = relationship(
        "ClusterNodeMembership",
        back_populates="node",
        cascade="all, delete-orphan"
    )

class KnowledgeCluster(Base):
    __tablename__ = "knowledge_clusters"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cluster_type: Mapped[str] = mapped_column(String(20), default="manual") # manual, ai_generated, intent_created
    center_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=True)
    
    # 簇级 AI 认知模型
    ai_model: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 簇特征
    metadata_info: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True) 
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    node_memberships: Mapped[List["ClusterNodeMembership"]] = relationship(
        "ClusterNodeMembership",
        back_populates="cluster",
        cascade="all, delete-orphan"
    )

class ClusterNodeMembership(Base):
    __tablename__ = "cluster_node_memberships"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_clusters.id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default="member") # center, member, peripheral
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cluster: Mapped["KnowledgeCluster"] = relationship("KnowledgeCluster", back_populates="node_memberships")
    node: Mapped["KnowledgeNode"] = relationship("KnowledgeNode", back_populates="cluster_memberships")

class KnowledgeNodeRelation(Base):
    __tablename__ = "knowledge_node_relations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    target_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    discovered_by: Mapped[str] = mapped_column(String(20), default="manual")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_node: Mapped["KnowledgeNode"] = relationship("KnowledgeNode", foreign_keys=[source_node_id], back_populates="outgoing_relations")
    target_node: Mapped["KnowledgeNode"] = relationship("KnowledgeNode", foreign_keys=[target_node_id], back_populates="incoming_relations")
