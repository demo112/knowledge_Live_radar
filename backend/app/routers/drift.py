import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.services.evolution.drift_detector import DriftDetector
from app.models.approval import Approval
from app.schemas.approval import ApprovalResponse

router = APIRouter(
    prefix="/drift",
    tags=["drift"]
)

@router.post("/detect/{pyramid_id}")
async def detect_drift(
    pyramid_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger drift detection for a pyramid.
    """
    detector = DriftDetector(db)
    
    # Run in background as it might take time
    background_tasks.add_task(detector.detect_drift, pyramid_id)
    
    return {"status": "accepted", "message": "Drift detection started in background"}

@router.get("/detections", response_model=List[ApprovalResponse])
async def list_drift_detections(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = "pending",
    db: AsyncSession = Depends(get_db)
):
    """
    List detected drift proposals.
    """
    query = (
        select(Approval)
        .where(Approval.type == "fix_drift")
        .order_by(desc(Approval.created_at))
        .offset(offset)
        .limit(limit)
    )
    
    if status:
        query = query.where(Approval.status == status)
        
    result = await db.execute(query)
    return result.scalars().all()
