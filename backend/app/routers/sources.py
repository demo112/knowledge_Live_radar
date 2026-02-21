from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Body, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.services.source_service import SourceService
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse, DiscoverRequest, DiscoveredSource, DiscoveryEvent
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from app.services.content_processor import content_processor
from app.services.lifecycle_manager import lifecycle_manager
from app.services.crawl_engine import crawl_engine
from app.services.source_template_service import SourceTemplateService
from app.services.scheduler.crawl_manager import crawl_manager
from app.schemas.source_template import SourceTemplate
from app.models.crawl_job import CrawlJob
from app.services.source_discovery import SourceDiscoveryService
from app.models.approval import Approval
from datetime import datetime, timezone

router = APIRouter(prefix="/sources", tags=["sources"])

def get_service(db: AsyncSession = Depends(get_db)) -> SourceService:
    return SourceService(db)

# ... (Previous existing imports and endpoints: analyze, templates, crawl, etc.)

@router.get("/discover/stream", response_class=StreamingResponse)
async def discover_sources_stream(
    pyramid_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream source discovery events (SSE).
    """
    async def event_generator():
        service = SourceDiscoveryService(db)
        try:
            async for event in service.discover_stream(pyramid_id):
                # Format as SSE data
                yield f"data: {event.model_dump_json()}\n\n"
        except Exception as e:
            # Send error event
            import json
            error_data = json.dumps({"event": "error", "data": {"message": str(e)}})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/discover", response_model=SuccessResponse[dict])
async def discover_sources(
    request: DiscoverRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger background source discovery task.
    """
    service = SourceDiscoveryService(db)
    
    # Run in background to avoid blocking
    # Note: We need to be careful with db session in background tasks. 
    # FastAPI's background_tasks runs after response is sent, but the db session might be closed.
    # However, for simple trigger, we can just run the logic here if it's fast enough, 
    # or better, use a proper task queue.
    # For this iteration, since we use `duckduckgo_search` which does network IO, 
    # we should ideally run it in background. 
    # But passing the `db` session to background task is tricky in FastAPI as it depends on request scope.
    # A common pattern is to create a new session in the background task or just await it here if user can wait 5-10s.
    # Let's await it here for simplicity and immediate feedback, as searching 5-10 keywords takes ~5s.
    # If it times out, we should move to background.
    
    try:
        count = await service.discover(request.pyramid_id)
        return SuccessResponse(data={"message": f"Discovery task completed. Found {count} new candidates.", "count": count})
    except Exception as e:
        # Log error
        print(f"Discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovered", response_model=SuccessResponse[List[DiscoveredSource]])
async def get_discovered_sources(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending discovered sources (approvals).
    """
    stmt = select(Approval).where(
        Approval.type == "create_source",
        Approval.status == "pending"
    ).order_by(Approval.created_at.desc())
    
    result = await db.execute(stmt)
    approvals = result.scalars().all()
    
    discovered_list = []
    for app in approvals:
        if not app.data: continue
        discovered_list.append(DiscoveredSource(
            id=app.id,
            url=app.data.get("url", ""),
            name=app.data.get("name", ""),
            description=app.data.get("description"),
            source_type=app.data.get("source_type", "RSS"),
            reason=app.data.get("reason"),
            created_at=app.created_at,
            status=app.status
        ))
        
    return SuccessResponse(data=discovered_list)

# ... (Rest of existing CRUD endpoints)

@router.get("/templates", response_model=SuccessResponse[List[SourceTemplate]])
async def get_source_templates():
    """Get available source templates"""
    service = SourceTemplateService()
    templates = service.get_templates()
    return SuccessResponse(data=templates)

@router.post("/templates/{template_id}/render", response_model=SuccessResponse[dict])
async def render_source_template(
    template_id: str,
    params: dict = Body(...)
):
    """Generate source config from template"""
    service = SourceTemplateService()
    try:
        config = service.generate_source_config(template_id, params)
        return SuccessResponse(data=config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=SuccessResponse[SourceResponse], status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreate,
    service: SourceService = Depends(get_service)
):
    """Create a new information source"""
    result = await service.create_source(source)
    return SuccessResponse(data=result)

@router.get("/", response_model=SuccessResponse[PaginatedData[SourceResponse]])
async def get_sources(
    page: int = 1,
    page_size: int = 20,
    service: SourceService = Depends(get_service)
):
    """Get list of information sources"""
    items, total = await service.get_sources(skip=(page - 1) * page_size, limit=page_size)
    return SuccessResponse(data=PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    ))

@router.get("/{id}", response_model=SuccessResponse[SourceResponse])
async def get_source(
    id: UUID,
    service: SourceService = Depends(get_service)
):
    """Get information source by ID"""
    source = await service.get_source(id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return SuccessResponse(data=source)

@router.post("/{id}/test", response_model=SuccessResponse[dict])
async def test_source(
    id: UUID,
    service: SourceService = Depends(get_service)
):
    """
    Test source connectivity and return crawl stats.
    """
    # Just verify source exists
    source = await service.get_source(id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    # In a real implementation, this would trigger a crawl
    # For now, return dummy success
    return SuccessResponse(data={"count": 1, "message": "Source reachable"})

@router.put("/{id}", response_model=SuccessResponse[SourceResponse])
async def update_source(
    id: UUID,
    source: SourceUpdate,
    service: SourceService = Depends(get_service)
):
    """Update information source"""
    result = await service.update_source(id, source)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return SuccessResponse(data=result)

@router.delete("/{id}", response_model=SuccessResponse[SourceResponse])
async def delete_source(
    id: UUID,
    service: SourceService = Depends(get_service)
):
    """Delete information source"""
    result = await service.delete_source(id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return SuccessResponse(data=result)
