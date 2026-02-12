from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidResponse, PyramidDetailResponse, PyramidNodeCreate, PyramidNodeResponse
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData

router = APIRouter(prefix="/pyramids", tags=["pyramids"])

def get_service(db: AsyncSession = Depends(get_db)) -> PyramidService:
    return PyramidService(db)

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
