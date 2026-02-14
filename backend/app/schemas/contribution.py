from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ContributionBase(BaseModel):
    input_type: str
    original_input: str
    status: str = "pending"

class ContributionCreate(ContributionBase):
    user_id: Optional[str] = None
    content_id: Optional[uuid.UUID] = None

class ContributionUpdate(BaseModel):
    status: Optional[str] = None
    extracted_content: Optional[str] = None
    extracted_concepts: Optional[List[Dict[str, Any]]] = None
    rejection_reason: Optional[str] = None

class ContributionResponse(ContributionBase):
    id: uuid.UUID
    user_id: Optional[str]
    extracted_content: Optional[str]
    extracted_concepts: Optional[List[Dict[str, Any]]]
    rejection_reason: Optional[str]
    content_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContributionStats(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    period_days: int
