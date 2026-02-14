from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ContentBase(BaseModel):
    title: str = Field(..., max_length=255)
    url: str
    summary: Optional[str] = None
    content_text: Optional[str] = None
    publish_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    concepts: Optional[List[Any]] = None
    ai_processed: bool = False

class ContentCreate(ContentBase):
    source_id: Optional[UUID] = None
    original_id: Optional[str] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    concepts: Optional[List[Any]] = None
    ai_processed: Optional[bool] = None

class ValidationResultResponse(BaseModel):
    overall_score: Optional[int] = None
    hard_result: Optional[dict[str, Any]] = None
    soft_result: Optional[dict[str, Any]] = None
    verified_at: datetime
    
    model_config = {"from_attributes": True}

class ContentResponse(ContentBase):
    id: UUID
    source_id: Optional[UUID] = None
    status: str
    content_hash: Optional[str] = None
    created_at: datetime
    validation_result: Optional[ValidationResultResponse] = None
    
    model_config = {"from_attributes": True}

class ContentWithRelationResponse(ContentResponse):
    relation_source: str
    relation_confidence: float
    relation_created_at: datetime
