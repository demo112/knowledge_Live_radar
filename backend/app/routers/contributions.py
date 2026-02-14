from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.database import get_db
from app.services.contribution.contribution_tracker import ContributionTracker
from app.schemas.contribution import ContributionResponse, ContributionStats

router = APIRouter(prefix="/contributions", tags=["contributions"])

@router.get("/", response_model=List[ContributionResponse])
async def list_contributions(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    tracker = ContributionTracker(db)
    if user_id:
        return await tracker.get_user_contributions(user_id, skip, limit)
    return await tracker.get_recent_contributions(limit)

@router.get("/stats", response_model=ContributionStats)
async def get_contribution_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    tracker = ContributionTracker(db)
    return await tracker.get_stats(days)

@router.get("/{id}", response_model=ContributionResponse)
async def get_contribution(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    tracker = ContributionTracker(db)
    contribution = await tracker.get_contribution(id)
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    return contribution
