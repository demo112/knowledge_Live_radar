from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.services.ai_monitor_service import AIMonitorService
from app.schemas.ai_monitor import (
    AIMetricOut, PaginatedAIMetrics, AIStatsOut, CleanMetricsIn, ModelStat
)

router = APIRouter(
    prefix="/ai-monitor",
    tags=["ai-monitor"],
    responses={404: {"description": "Not found"}},
)

@router.get("/metrics", response_model=PaginatedAIMetrics)
async def read_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    module: Optional[str] = Query(None, description="Filter by module"),
    model: Optional[str] = Query(None, description="Filter by model"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status: Optional[str] = Query(None, description="Filter by status (success/error)"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    db: AsyncSession = Depends(get_db)
):
    service = AIMonitorService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_metrics(
        skip=skip, 
        limit=page_size, 
        module=module,
        model=model,
        provider=provider,
        status=status,
        start_time=start_time,
        end_time=end_time
    )
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/stats", response_model=AIStatsOut)
async def read_stats(
    start_time: Optional[datetime] = Query(None, description="Start time for aggregation"),
    end_time: Optional[datetime] = Query(None, description="End time for aggregation"),
    db: AsyncSession = Depends(get_db)
):
    service = AIMonitorService(db)
    stats = await service.get_aggregated_stats(start_time=start_time, end_time=end_time)
    return stats

@router.post("/clean")
async def clean_metrics(
    payload: CleanMetricsIn,
    db: AsyncSession = Depends(get_db)
):
    service = AIMonitorService(db)
    deleted_count = await service.clean_old_metrics(days=payload.days)
    return {"deleted_count": deleted_count}
