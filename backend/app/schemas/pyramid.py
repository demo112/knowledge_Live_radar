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

class PyramidNodeCreate(PyramidNodeBase):
    parent_id: Optional[UUID] = None

class PyramidNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None

class PyramidNodeMove(BaseModel):
    new_parent_id: Optional[UUID] = None
    new_sort_order: Optional[int] = None

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
