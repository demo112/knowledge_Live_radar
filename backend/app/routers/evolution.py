from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.evolution_engine import EvolutionEngine
from app.models.content import ContentItem
from app.schemas.common import SuccessResponse
from app.services.batch_classification_service import batch_classification_service

router = APIRouter(prefix="/evolution", tags=["evolution"])

def get_evolution_engine(db: AsyncSession = Depends(get_db)) -> EvolutionEngine:
    return EvolutionEngine(db)

@router.post("/classify/batch", response_model=SuccessResponse[dict])
async def batch_classify_content(
    background_tasks: BackgroundTasks,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger batch auto-classification for unclassified content (Background Task).
    """
    result = await batch_classification_service.start_batch_classification(
        batch_size=limit,
        background_tasks=background_tasks
    )
    
    return SuccessResponse(data=result)

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
        raise HTTPException(status_code=404, detail="未找到内容")
        
    count = await engine.auto_classify_content(content)
    return SuccessResponse(data=count)
