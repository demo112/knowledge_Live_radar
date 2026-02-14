from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.content_management_service import ContentManagementService, run_batch_summarization
from app.services.metabolism_service import MetabolismService
from app.schemas.content_management import (
    BatchCleanRequest, BatchCleanData,
    BatchSummarizeRequest, BatchSummarizeData,
    BatchDeleteRequest, BatchDeleteData,
    MetabolismRunResponse, MetabolismSuggestionResponse,
    MetabolismCleanupRequest, MetabolismCleanupResponse
)

router = APIRouter(
    prefix="/content-management",
    tags=["content-management"]
)

@router.post("/clean", response_model=BatchCleanData)
async def batch_clean(
    request: BatchCleanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan and clean content based on Chinese ratio and AI relevance.
    """
    service = ContentManagementService(db)
    return await service.batch_clean(
        dry_run=request.dry_run,
        chinese_ratio_threshold=request.chinese_ratio_threshold
    )

@router.post("/summarize", response_model=BatchSummarizeData)
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
    result = await service.batch_summarize(
        target_ids=request.target_ids,
        overwrite=request.overwrite
    )
    
    # Add background task
    background_tasks.add_task(
        run_batch_summarization,
        target_ids=request.target_ids,
        overwrite=request.overwrite
    )
    
    return result

@router.post("/delete", response_model=BatchDeleteData)
async def batch_delete(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch delete content items.
    """
    service = ContentManagementService(db)
    return await service.batch_delete(ids=request.ids)

@router.post("/metabolism/run", response_model=MetabolismRunResponse)
async def run_metabolism(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger the content metabolism process.
    """
    service = MetabolismService(db)
    stats = await service.process_metabolism()
    return MetabolismRunResponse(**stats)

@router.get("/metabolism/suggestions", response_model=MetabolismSuggestionResponse)
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

@router.post("/metabolism/cleanup", response_model=MetabolismCleanupResponse)
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
