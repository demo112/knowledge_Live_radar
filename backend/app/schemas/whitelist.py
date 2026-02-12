from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class DomainCheckRequest(BaseModel):
    url: str

class DomainWhitelistCreate(BaseModel):
    domain: str
    credibility: int = Field(default=50, ge=0, le=100)
    reason: Optional[str] = None

class DomainWhitelistResponse(BaseModel):
    id: UUID
    domain: str
    credibility: int
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DiscoveredDomainResponse(BaseModel):
    id: UUID
    domain: str
    occurrence_count: int
    first_seen_at: datetime
    last_seen_at: datetime
    evaluation_status: str
    has_rss: bool
    proposal_id: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)

class PaginatedWhitelist(BaseModel):
    items: List[DomainWhitelistResponse]
    total: int
    page: int
    page_size: int

class PaginatedDiscovered(BaseModel):
    items: List[DiscoveredDomainResponse]
    total: int
    page: int
    page_size: int
