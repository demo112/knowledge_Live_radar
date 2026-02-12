from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pyramid_service import PyramidService
from app.services.snapshot_service import SnapshotService
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidResponse, PyramidDetailResponse, PyramidNodeCreate, PyramidNodeResponse
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from app.schemas.snapshot import SnapshotSummaryResponse

router = APIRouter(prefix="/pyramids", tags=["pyramids"])

from app.services.template_service import TemplateService

def get_service(db: AsyncSession = Depends(get_db)) -> PyramidService:
    return PyramidService(db)

def get_template_service(service: PyramidService = Depends(get_service)) -> TemplateService:
    return TemplateService(service)

@router.get("/templates", response_model=SuccessResponse[List[dict]])
async def get_templates(
    service: TemplateService = Depends(get_template_service)
):
    """Get available pyramid templates"""
    templates = service.get_templates()
    return SuccessResponse(data=templates)

@router.post("/from-template/{template_id}", response_model=SuccessResponse[PyramidDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_pyramid_from_template(
    template_id: str,
    name: str = None,
    service: TemplateService = Depends(get_template_service)
):
    """Create a new pyramid from a template"""
    pyramid = await service.create_from_template(template_id, name)
    # Re-fetch details to include nodes
    # Assuming service returns the pyramid object but nodes are lazy loaded or need separate fetch if not eagerly loaded in create_from_template return
    # The create_from_template returns the pyramid object.
    # We might want to return full details.
    return SuccessResponse(data=pyramid)

@router.post("", response_model=SuccessResponse[PyramidResponse], status_code=status.HTTP_201_CREATED)
async def create_pyramid(
    schema: PyramidCreate,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.create_pyramid(schema)
    return SuccessResponse(data=pyramid)

@router.get("", response_model=PaginatedResponse[PyramidResponse])
async def get_pyramids(
    skip: int = 0,
    limit: int = 100,
    service: PyramidService = Depends(get_service)
):
    items = await service.get_all_pyramids(skip, limit)
    # Mock total count for now or implement count in repo
    total = len(items) 
    return PaginatedResponse(data=PaginatedData(items=items, total=total, page=skip//limit + 1 if limit else 1, page_size=limit))

@router.get("/{id}", response_model=SuccessResponse[PyramidDetailResponse])
async def get_pyramid(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.get_pyramid_details(id)
    return SuccessResponse(data=pyramid)

@router.put("/{id}", response_model=SuccessResponse[PyramidResponse])
async def update_pyramid(
    id: UUID,
    schema: PyramidUpdate,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.update_pyramid(id, schema)
    return SuccessResponse(data=pyramid)

@router.delete("/{id}", response_model=SuccessResponse[PyramidResponse])
async def delete_pyramid(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.delete_pyramid(id)
    return SuccessResponse(data=pyramid)

@router.post("/{id}/nodes", response_model=SuccessResponse[PyramidNodeResponse], status_code=status.HTTP_201_CREATED)
async def add_node(
    id: UUID,
    schema: PyramidNodeCreate,
    service: PyramidService = Depends(get_service)
):
    node = await service.add_node(id, schema)
    return SuccessResponse(data=node)

@router.get("/{id}/snapshots", response_model=SuccessResponse[List[SnapshotSummaryResponse]])
async def get_snapshots(
    id: UUID,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    snapshot_service = SnapshotService(db)
    snapshots = await snapshot_service.get_snapshots_by_pyramid(id, skip, limit)
    return SuccessResponse(data=snapshots)
