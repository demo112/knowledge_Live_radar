from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.services.source_service import SourceService
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from fastapi import HTTPException
from app.services.content_processor import content_processor
from app.services.lifecycle_manager import lifecycle_manager
from app.services.crawl_engine import crawl_engine
from app.services.source_template_service import SourceTemplateService
from app.services.scheduler.crawl_manager import crawl_manager
from app.schemas.source_template import SourceTemplate
from app.models.crawl_job import CrawlJob
from datetime import datetime, timezone
from fastapi import Body

router = APIRouter(prefix="/sources", tags=["sources"])

def get_service(db: AsyncSession = Depends(get_db)) -> SourceService:
    return SourceService(db)

from app.core.ai.facade import ai_facade
from app.schemas.ai import SourceAnalyzeRequest, SourceAnalyzeResponse

@router.post("/analyze", response_model=SuccessResponse[SourceAnalyzeResponse])
async def analyze_source(
    request: SourceAnalyzeRequest
):
    """
    AI Analyze a source URL before adding it.
    """
    # In a real scenario, we might want to fetch content first (CrawlEngine)
    # But AIFacade.analyze_source takes url and sample_content.
    # So we need to fetch here or inside facade.
    # The Facade calls ContentProcessor which takes sample_content.
    # So we need to crawl here.
    
    # Let's use CrawlEngine to preview
    preview = await crawl_engine.preview_source(request.url)
    sample_content = preview.content if preview else ""
    
    analysis = await ai_facade.analyze_source(request.url, sample_content)
    return SuccessResponse(data=analysis)

@router.get("/templates", response_model=SuccessResponse[List[SourceTemplate]])
async def get_source_templates():
    """获取所有信息源配置模板"""
    service = SourceTemplateService()
    templates = service.get_templates()
    return SuccessResponse(data=templates)

@router.post("/templates/{template_id}/render", response_model=SuccessResponse[dict])
async def render_source_template(
    template_id: str,
    params: dict = Body(...)
):
    """根据模板和参数生成信息源配置"""
    service = SourceTemplateService()
    try:
        config = service.generate_source_config(template_id, params)
        return SuccessResponse(data=config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/crawl", response_model=SuccessResponse[dict])
async def crawl_source_manual(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = SourceService(db)
    source = await service.get_source(id)
    if not source:
        raise HTTPException(status_code=404, detail="未找到信息源")
    
    # Create PENDING job
    job = CrawlJob(
        source_id=source.id,
        status="PENDING",
        created_at=datetime.now(timezone.utc)
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Enqueue with high priority (0)
    await crawl_manager.add_task(source.id, job_id=job.id, priority=0)
    
    return SuccessResponse(data={"job_id": str(job.id), "status": "PENDING", "items_new": 0})

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

@router.get("/{id}/history", response_model=SuccessResponse[List[dict]])
async def get_source_history(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取信息源的抓取历史"""
    stmt = select(CrawlJob).where(CrawlJob.source_id == id).order_by(desc(CrawlJob.created_at)).limit(20)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    data = []
    for job in jobs:
        data.append({
            "id": str(job.id),
            "status": job.status,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
            "items_fetched": job.items_fetched,
            "items_new": job.items_new,
            "error_message": job.error_message
        })
        
    return SuccessResponse(data=data)

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
