from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class DiscoveryStage(str, Enum):
    EXTRACT = "extract"
    SEARCH = "search"
    FILTER = "filter"
    PROPOSAL = "proposal"
    FINISH = "finish"

class DiscoveryStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DiscoveryEvent(BaseModel):
    event: str = Field(..., description="Event type: stage_update, log, progress, result, error")
    data: Dict[str, Any]

class InformationSourceBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(RSS|API|WEB|USER|WECHAT_MP|BILIBILI_USER|JUEJIN_COLUMN)$")
    url: str
    config: Optional[dict[str, Any]] = None
    template_id: Optional[str] = None
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

class DiscoverRequest(BaseModel):
    pyramid_id: Optional[UUID] = Field(None, description="Optional pyramid ID to scope discovery")

class DiscoveredSource(BaseModel):
    id: UUID
    url: str
    name: str
    description: Optional[str] = None
    source_type: str
    reason: Optional[str] = None
    created_at: datetime
    status: str

    model_config = {"from_attributes": True}
