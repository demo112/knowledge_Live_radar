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

class ContentCreate(ContentBase):
    source_id: Optional[UUID] = None
    original_id: Optional[str] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class ContentResponse(ContentBase):
    id: UUID
    source_id: Optional[UUID]
    status: str
    content_hash: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}
