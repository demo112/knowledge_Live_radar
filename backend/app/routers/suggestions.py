from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.ai_suggestion import AISuggestion
from app.services.suggestion_executor import suggestion_executor

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

@router.get("/", response_model=List[dict])
async def list_suggestions(
    pyramid_id: Optional[UUID] = None,
    source_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取建议列表"""
    stmt = select(AISuggestion)
    
    if pyramid_id:
        stmt = stmt.where(AISuggestion.pyramid_id == pyramid_id)
    if source_id:
        stmt = stmt.where(AISuggestion.source_id == source_id)
    if status:
        stmt = stmt.where(AISuggestion.status == status)
        
    stmt = stmt.order_by(AISuggestion.created_at.desc())
    result = await db.execute(stmt)
    suggestions = result.scalars().all()
    
    return [
        {
            "id": str(s.id),
            "action_type": s.action_type,
            "target_type": s.target_type,
            "target_id": str(s.target_id) if s.target_id else None,
            "target_name": s.target_name,
            "reason": s.reason,
            "params": s.params,
            "confidence": s.confidence,
            "status": s.status,
            "pyramid_id": str(s.pyramid_id) if s.pyramid_id else None,
            "source_id": str(s.source_id) if s.source_id else None,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
        }
        for s in suggestions
    ]

@router.post("/{id}/approve")
async def approve_suggestion(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """审批建议"""
    executor = suggestion_executor(db)
    result = await executor.approve(str(id), db)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"]["message"]
        )
        
    return result

@router.post("/{id}/reject")
async def reject_suggestion(
    id: UUID,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """拒绝建议"""
    executor = suggestion_executor(db)
    result = await executor.reject(str(id), db, reason)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"]["message"]
        )
        
    return result

@router.post("/{id}/execute")
async def execute_suggestion(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """执行建议"""
    executor = suggestion_executor(db)
    result = await executor.execute(str(id), db)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"]["message"]
        )
        
    return result
