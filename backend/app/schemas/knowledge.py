from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Node Relation Schemas
class KnowledgeNodeRelationBase(BaseModel):
    target_node_id: UUID
    relation_type: str = "related"
    weight: float = 1.0
    confidence: float = 1.0
    evidence: Optional[Dict[str, Any]] = None
    discovered_by: str = "manual"

class KnowledgeNodeRelationCreate(KnowledgeNodeRelationBase):
    pass

class KnowledgeNodeRelationResponse(KnowledgeNodeRelationBase):
    id: UUID
    source_node_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Node Schemas
class KnowledgeNodeBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    node_type: str = "concept"
    ai_model: Optional[Dict[str, Any]] = None
    concept_id: Optional[UUID] = None
    status: str = "active"

class KnowledgeNodeCreate(KnowledgeNodeBase):
    pass

class KnowledgeNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    node_type: Optional[str] = None
    ai_model: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class KnowledgeNodeResponse(KnowledgeNodeBase):
    id: UUID
    health_score: int
    content_count: int
    last_content_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    outgoing_relations: List[KnowledgeNodeRelationResponse] = []
    incoming_relations: List[KnowledgeNodeRelationResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Cluster Membership Schemas
class ClusterNodeMembershipBase(BaseModel):
    node_id: UUID
    role: str = "member"
    weight: float = 1.0

class ClusterNodeMembershipCreate(ClusterNodeMembershipBase):
    pass

class ClusterNodeMembershipResponse(ClusterNodeMembershipBase):
    cluster_id: UUID
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Cluster Schemas
class KnowledgeClusterBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    cluster_type: str = "manual"
    center_node_id: Optional[UUID] = None
    ai_model: Optional[Dict[str, Any]] = None
    metadata_info: Optional[Dict[str, Any]] = None
    status: str = "active"

class KnowledgeClusterCreate(KnowledgeClusterBase):
    pass

class KnowledgeClusterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    center_node_id: Optional[UUID] = None
    ai_model: Optional[Dict[str, Any]] = None
    metadata_info: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class KnowledgeClusterResponse(KnowledgeClusterBase):
    id: UUID
    health_score: int
    node_count: int
    created_at: datetime
    updated_at: datetime
    
    node_memberships: List[ClusterNodeMembershipResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class KnowledgeGraphNodeResponse(KnowledgeNodeBase):
    id: UUID
    health_score: int
    content_count: int
    last_content_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class KnowledgeGraphResponse(BaseModel):
    root_id: UUID
    nodes: List[KnowledgeGraphNodeResponse]
    edges: List[KnowledgeNodeRelationResponse]
