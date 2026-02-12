from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class InformationSourceBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(RSS|API|WEB|USER)$")
    url: str
    config: Optional[dict[str, Any]] = None
    check_interval: int = 3600

class SourceCreate(InformationSourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    check_interval: Optional[int] = None
    status: Optional[str] = None

class SourceResponse(InformationSourceBase):
    id: UUID
    status: str
    health_score: int
    last_crawled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
