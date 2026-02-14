from fastapi import APIRouter, Depends, BackgroundTasks, Query
from app.services.batch_classification_service import batch_classification_service
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/classification", tags=["classification"])

@router.post("/batch", response_model=SuccessResponse)
async def trigger_batch_classification(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(10, ge=1, le=100)
):
    """
    Trigger batch classification for unclassified content.
    Runs in background.
    """
    result = await batch_classification_service.start_batch_classification(batch_size, background_tasks)
    return SuccessResponse(data=result)
