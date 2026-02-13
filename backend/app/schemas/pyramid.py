from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Node Schemas
class PyramidNodeBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    level: int = 0
    sort_order: int = 0
    health_score: int = 100
    status: str = "pending"

class PyramidNodeCreate(PyramidNodeBase):
    parent_id: Optional[UUID] = None

class PyramidNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None

class PyramidNodeMove(BaseModel):
    new_parent_id: Optional[UUID] = None
    new_sort_order: Optional[int] = None

# Node Relation Schemas
class NodeRelationBase(BaseModel):
    target_node_id: UUID
    relation_type: str = "related"

class NodeRelationCreate(NodeRelationBase):
    pass

class NodeRelationResponse(NodeRelationBase):
    id: UUID
    source_node_id: UUID
    
    model_config = {"from_attributes": True}

# Node Operation Schemas
class NodeSplitRequest(BaseModel):
    children: List[PyramidNodeCreate]

class NodeMergeRequest(BaseModel):
    source_node_ids: List[UUID]
    new_node_name: str
    new_node_description: Optional[str] = None

class NodeLinkRequest(NodeRelationCreate):
    pass

class PyramidNodeResponse(PyramidNodeBase):
    id: UUID
    pyramid_id: UUID
    parent_id: Optional[UUID]
    path: str
    
    model_config = {"from_attributes": True}

# Pyramid Schemas
class PyramidBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class PyramidCreate(PyramidBase):
    pass

class PyramidUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class PyramidResponse(PyramidBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class PyramidDetailResponse(PyramidResponse):
    nodes: List[PyramidNodeResponse] = []
