from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.source_service import SourceService
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from fastapi import HTTPException
from app.services.content_processor import content_processor
from app.services.lifecycle_manager import lifecycle_manager
from app.services.crawl_engine import crawl_engine

router = APIRouter(prefix="/sources", tags=["sources"])

def get_service(db: AsyncSession = Depends(get_db)) -> SourceService:
    return SourceService(db)

@router.post("/{id}/crawl", response_model=SuccessResponse[dict])
async def crawl_source_manual(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = SourceService(db)
    source = await service.get_source(id)
    if not source:
        raise HTTPException(status_code=404, detail="未找到信息源")
    
    job = await content_processor.process_source(source, db)
    await lifecycle_manager.update_source_status(source, job, db)
    
    return SuccessResponse(data={"job_id": str(job.id), "status": job.status, "items_new": job.items_new})

@router.post("/{id}/test", response_model=SuccessResponse[dict])
async def test_source_manual(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = SourceService(db)
    source = await service.get_source(id)
    if not source:
        raise HTTPException(status_code=404, detail="未找到信息源")
        
    try:
        items = await crawl_engine.crawl_source(source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"抓取失败: {str(e)}")
        
    # Return limited items to avoid huge response
    return SuccessResponse(data={"items": items[:10], "count": len(items)})

@router.post("", response_model=SuccessResponse[SourceResponse], status_code=status.HTTP_201_CREATED)
async def create_source(
    schema: SourceCreate,
    service: SourceService = Depends(get_service)
):
    source = await service.create_source(schema)
    return SuccessResponse(data=source)

@router.get("", response_model=PaginatedResponse[SourceResponse])
async def get_sources(
    skip: int = 0,
    limit: int = 100,
    service: SourceService = Depends(get_service)
):
    items = await service.get_all_sources(skip, limit)
    total = len(items)
    return PaginatedResponse(data=PaginatedData(items=items, total=total, page=skip//limit + 1 if limit else 1, page_size=limit))

@router.get("/{id}", response_model=SuccessResponse[SourceResponse])
async def get_source(
    id: UUID,
    service: SourceService = Depends(get_service)
):
    source = await service.get_source(id)
    return SuccessResponse(data=source)

@router.put("/{id}", response_model=SuccessResponse[SourceResponse])
async def update_source(
    id: UUID,
    schema: SourceUpdate,
    service: SourceService = Depends(get_service)
):
    source = await service.update_source(id, schema)
    return SuccessResponse(data=source)

@router.delete("/{id}", response_model=SuccessResponse[SourceResponse])
async def delete_source(
    id: UUID,
    service: SourceService = Depends(get_service)
):
    source = await service.delete_source(id)
    return SuccessResponse(data=source)
