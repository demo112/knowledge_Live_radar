from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidNodeUpdate, PyramidNodeResponse, PyramidNodeMove
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/nodes", tags=["nodes"])

def get_service(db: AsyncSession = Depends(get_db)) -> PyramidService:
    return PyramidService(db)

@router.post("/{id}/move", response_model=SuccessResponse[PyramidNodeResponse])
async def move_node(
    id: UUID,
    schema: PyramidNodeMove,
    service: PyramidService = Depends(get_service)
):
    """
    Move a node to a new parent or reorder it.
    """
    node = await service.move_node(id, schema.new_parent_id, schema.new_sort_order)
    return SuccessResponse(data=node)

@router.get("/{id}", response_model=SuccessResponse[PyramidNodeResponse])
async def get_node(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    node = await service.get_node(id)
    return SuccessResponse(data=node)

@router.put("/{id}", response_model=SuccessResponse[PyramidNodeResponse])
async def update_node(
    id: UUID,
    schema: PyramidNodeUpdate,
    service: PyramidService = Depends(get_service)
):
    node = await service.update_node(id, schema)
    return SuccessResponse(data=node)

@router.delete("/{id}", response_model=SuccessResponse[PyramidNodeResponse])
async def delete_node(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    node = await service.delete_node(id)
    return SuccessResponse(data=node)
