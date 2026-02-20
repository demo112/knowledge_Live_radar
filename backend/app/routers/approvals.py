from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.approval_service import ApprovalService
from app.services.impact_analyzer import ImpactAnalyzer
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

@router.get("/", response_model=SuccessResponse[List[ApprovalResponse]])
async def get_approvals(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    service: ApprovalService = Depends(get_service)
):
    approvals = await service.get_approvals(status, skip, limit)
    return SuccessResponse(data=approvals)

@router.get("/pending", response_model=SuccessResponse[List[ApprovalResponse]])
async def get_pending_approvals(
    skip: int = 0,
    limit: int = 100,
    service: ApprovalService = Depends(get_service)
):
    # Keep this for backward compatibility if needed, or redirect
    approvals = await service.get_approvals("pending", skip, limit)
    return SuccessResponse(data=approvals)

@router.get("/queue", response_model=SuccessResponse[List[ApprovalResponse]])
async def get_approval_queue(
    skip: int = 0,
    limit: int = 100,
    service: ApprovalService = Depends(get_service)
):
    """
    Get approval queue (alias for pending approvals).
    """
    approvals = await service.get_approvals("pending", skip, limit)
    return SuccessResponse(data=approvals)

@router.get("/{id}", response_model=SuccessResponse[ApprovalResponse])
async def get_approval(
    id: UUID,
    service: ApprovalService = Depends(get_service)
):
    approval = await service.get_approval(id)
    if not approval:
        raise HTTPException(status_code=404, detail="未找到审批提案")
    return SuccessResponse(data=approval)

@router.post("/{id}/review", response_model=SuccessResponse[ApprovalResponse])
async def review_approval(
    id: UUID,
    schema: ApprovalUpdate,
    service: ApprovalService = Depends(get_service)
):
    approval = await service.review_approval(id, schema)
    if not approval:
        raise HTTPException(status_code=404, detail="未找到审批提案")
    return SuccessResponse(data=approval)

@router.post("/{id}/execute", response_model=SuccessResponse[bool])
async def execute_approval(
    id: UUID,
    user_id: str = "current_user", # In real app, get from auth context
    service: ApprovalService = Depends(get_service)
):
    success = await service.execute_approval(id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="执行失败。请确保提案已批准且有效。")
    return SuccessResponse(data=success)

@router.post("/{id}/rollback", response_model=SuccessResponse[bool])
async def rollback_approval(
    id: UUID,
    service: ApprovalService = Depends(get_service)
):
    success = await service.rollback_execution(id)
    if not success:
        raise HTTPException(status_code=400, detail="回滚失败。请确保提案已执行且存在快照。")
    return SuccessResponse(data=success)

@router.get("/{id}/impact", response_model=SuccessResponse[dict])
async def get_approval_impact(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = ApprovalService(db)
    approval = await service.get_approval(id)
    if not approval:
        raise HTTPException(status_code=404, detail="未找到审批提案")
        
    analyzer = ImpactAnalyzer(db)
    impact = await analyzer.analyze_impact(approval)
    
    # Commit the analysis result
    db.add(approval)
    await db.commit()
    
    return SuccessResponse(data=impact)
