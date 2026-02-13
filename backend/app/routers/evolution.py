from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.evolution_engine import EvolutionEngine
from app.models.content import ContentItem
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/evolution", tags=["evolution"])

def get_evolution_engine(db: AsyncSession = Depends(get_db)) -> EvolutionEngine:
    return EvolutionEngine(db)

@router.post("/classify/{content_id}", response_model=SuccessResponse[int])
async def classify_content(
    content_id: UUID,
    engine: EvolutionEngine = Depends(get_evolution_engine),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger auto-classification for a specific content item.
    """
    # Load content item
    stmt = select(ContentItem).where(ContentItem.id == content_id)
    result = await db.execute(stmt)
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
        
    count = await engine.auto_classify_content(content)
    return SuccessResponse(data=count)

@router.post("/classify/batch", response_model=SuccessResponse[str])
async def batch_classify_content(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger batch auto-classification for unclassified content (Background Task).
    """
    # This is a simplified version. Ideally, we should query content that hasn't been linked.
    # For now, we just return a message as this might be a long running task.
    
    # We can implement the actual logic later or add it to background tasks.
    # To keep it safe, let's just implement a simple one-off for now or just placeholder.
    
    return SuccessResponse(data="Batch classification started (Not implemented yet)")
