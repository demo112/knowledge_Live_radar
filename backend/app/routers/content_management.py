from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.content_management_service import ContentManagementService, run_batch_summarization
from app.services.metabolism_service import MetabolismService
from app.schemas.content_management import (
    BatchCleanRequest, BatchCleanData, BatchCleanResponse,
    BatchSummarizeRequest, BatchSummarizeData, BatchSummarizeResponse,
    BatchDeleteRequest, BatchDeleteData, BatchDeleteResponse,
    MetabolismRunResponse, MetabolismSuggestionResponse,
    MetabolismCleanupRequest, MetabolismCleanupResponse
)

router = APIRouter(
    prefix="/contents/batch",
    tags=["content-management"]
)

@router.post("/clean", response_model=BatchCleanResponse)
async def batch_clean(
    request: BatchCleanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan and clean content based on Chinese ratio and AI relevance.
    """
    service = ContentManagementService(db)
    data = await service.batch_clean(
        dry_run=request.dry_run,
        chinese_ratio_threshold=request.chinese_ratio_threshold
    )
    return BatchCleanResponse(data=data)

@router.post("/summarize", response_model=BatchSummarizeResponse)
async def batch_summarize(
    request: BatchSummarizeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger batch summarization for selected items or all items.
    """
    service = ContentManagementService(db)
    
    # Check trigger count first (synchronously within the request)
    data = await service.batch_summarize(
        target_ids=request.target_ids,
        overwrite=request.overwrite
    )
    
    # Add background task
    background_tasks.add_task(
        run_batch_summarization,
        target_ids=request.target_ids,
        overwrite=request.overwrite
    )
    
    return BatchSummarizeResponse(data=data)

@router.post("/delete", response_model=BatchDeleteResponse)
async def batch_delete(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch delete content items.
    """
    service = ContentManagementService(db)
    data = await service.batch_delete(ids=request.ids)
    return BatchDeleteResponse(data=data)

# --- Metabolism Routes ---
metabolism_router = APIRouter(
    prefix="/content-management/metabolism",
    tags=["metabolism"]
)

@metabolism_router.post("/run", response_model=MetabolismRunResponse)
async def run_metabolism(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger the content metabolism process.
    """
    service = MetabolismService(db)
    stats = await service.process_metabolism()
    return MetabolismRunResponse(**stats)

@metabolism_router.get("/suggestions", response_model=MetabolismSuggestionResponse)
async def get_metabolism_suggestions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of items suggested for deletion.
    """
    service = MetabolismService(db)
    items = await service.get_cleanup_suggestions(limit=limit)
    return MetabolismSuggestionResponse(items=items)

@metabolism_router.post("/cleanup", response_model=MetabolismCleanupResponse)
async def execute_metabolism_cleanup(
    request: MetabolismCleanupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute soft deletion for suggested items.
    """
    service = MetabolismService(db)
    count = await service.execute_cleanup(item_ids=request.ids)
    return MetabolismCleanupResponse(deleted_count=count)
