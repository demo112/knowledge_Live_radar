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

class BatchReviewRequest(BaseModel):
    ids: list[UUID]
    action: str  # "approve" | "reject"
    reason: Optional[str] = "Batch operation"

class BatchReviewResult(BaseModel):
    success_count: int
    failure_count: int
    failures: list[Dict[str, Any]] # [{"id": "...", "error": "..."}]

class CleanupRequest(BaseModel):
    reason: str = "Batch Cleanup"

class CleanupResult(BaseModel):
    count: int
    message: str
