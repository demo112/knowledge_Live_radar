from uuid import UUID
from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

class ApprovalBase(BaseModel):
    type: str
    target_id: Optional[UUID] = None
    data: Optional[Dict[str, Any]] = None
    applicant_id: Optional[str] = None
    source_content_id: Optional[UUID] = None
    generated_by: Optional[str] = "user"
    reason: Optional[str] = None
    confidence_score: Optional[float] = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalUpdate(BaseModel):
    status: str # approved, rejected
    reviewer_id: Optional[str] = None
    review_comment: Optional[str] = None

class ApprovalResponse(ApprovalBase):
    id: UUID
    status: str
    reviewer_id: Optional[str]
    review_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
