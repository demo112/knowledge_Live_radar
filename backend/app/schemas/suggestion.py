from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class SuggestionBase(BaseModel):
    type: str
    action_type: str
    target_type: str
    target_id: Optional[UUID] = None
    target_name: Optional[str] = None
    reason: str
    params: Dict[str, Any]
    status: str = "pending"
    confidence: Optional[float] = None
    input_hash: Optional[str] = None
    reasoning: Optional[str] = None

class SuggestionCreate(SuggestionBase):
    input_hash: str
    pyramid_id: Optional[UUID] = None
    source_id: Optional[UUID] = None

class SuggestionResponse(SuggestionBase):
    id: UUID
    created_at: datetime
    expires_at: Optional[datetime] = None
    pyramid_id: Optional[UUID] = None
    source_id: Optional[UUID] = None

    model_config = {"from_attributes": True}

class SuggestionRejectRequest(BaseModel):
    reason: Optional[str] = None
