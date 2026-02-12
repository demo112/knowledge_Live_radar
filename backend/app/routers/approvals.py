from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.approval_service import ApprovalService
from app.services.decision_executor import DecisionExecutor
from app.schemas.approval import ApprovalCreate, ApprovalUpdate, ApprovalResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])

def get_service(db: AsyncSession = Depends(get_db)) -> ApprovalService:
    return ApprovalService(db)

@router.post("/", response_model=SuccessResponse[ApprovalResponse], status_code=status.HTTP_201_CREATED)
async def create_approval(
    schema: ApprovalCreate,
    service: ApprovalService = Depends(get_service)
):
    approval = await service.create_approval(schema)
    return SuccessResponse(data=approval)

@router.get("/pending", response_model=SuccessResponse[List[ApprovalResponse]])
async def get_pending_approvals(
    skip: int = 0,
    limit: int = 100,
    service: ApprovalService = Depends(get_service)
):
    approvals = await service.get_pending_approvals(skip, limit)
    return SuccessResponse(data=approvals)

@router.get("/{id}", response_model=SuccessResponse[ApprovalResponse])
async def get_approval(
    id: UUID,
    service: ApprovalService = Depends(get_service)
):
    approval = await service.get_approval(id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return SuccessResponse(data=approval)

@router.post("/{id}/review", response_model=SuccessResponse[ApprovalResponse])
async def review_approval(
    id: UUID,
    schema: ApprovalUpdate,
    service: ApprovalService = Depends(get_service)
):
    approval = await service.review_approval(id, schema)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return SuccessResponse(data=approval)

@router.post("/{id}/execute", response_model=SuccessResponse[bool])
async def execute_approval(
    id: UUID,
    user_id: str = "current_user", # In real app, get from auth context
    db: AsyncSession = Depends(get_db)
):
    executor = DecisionExecutor(db)
    success = await executor.execute_approval(id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Execution failed. Ensure approval is approved and valid.")
    return SuccessResponse(data=success)
