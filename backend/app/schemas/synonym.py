from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class SynonymBase(BaseModel):
    canonical_term: str
    synonym: str
    source: str = "manual"
    confidence: float = 1.0
    is_active: bool = True

class SynonymCreate(SynonymBase):
    pass

class SynonymBulkCreate(BaseModel):
    mappings: List[SynonymCreate]

class SynonymResponse(SynonymBase):
    id: uuid.UUID
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
