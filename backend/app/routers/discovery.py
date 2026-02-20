from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auto_discovery import auto_discovery
from app.services.discovery_service import DiscoveryService
from app.schemas.common import SuccessResponse

class DiscoveryRequest(BaseModel):
    url: str

class DiscoveryResponse(BaseModel):
    title: str
    url: str
    type: str

class NodeRelationDiscoveryRequest(BaseModel):
    pyramid_id: Optional[UUID] = None
    similarity_threshold: float = 0.7
    limit: int = 50

class ContentClusterDiscoveryRequest(BaseModel):
    batch_size: int = 50
    similarity_threshold: float = 0.8

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.post("/sources", response_model=SuccessResponse[List[DiscoveryResponse]])
@router.post("/discover", response_model=SuccessResponse[List[DiscoveryResponse]], deprecated=True)
async def discover_sources(request: DiscoveryRequest):
    """
    Discover potential sources from a URL.
    """
    results = await auto_discovery.discover_from_url(request.url)
    return SuccessResponse(data=results)

@router.post("/relations", response_model=SuccessResponse[List[Dict[str, Any]]])
async def discover_node_relations(
    request: NodeRelationDiscoveryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover potential relations between knowledge nodes based on vector similarity.
    """
    service = DiscoveryService(db)
    results = await service.discover_node_relations(
        pyramid_id=request.pyramid_id,
        similarity_threshold=request.similarity_threshold,
        limit=request.limit
    )
    return SuccessResponse(data=results)

@router.post("/clusters", response_model=SuccessResponse[List[Dict[str, Any]]])
async def discover_content_clusters(
    request: ContentClusterDiscoveryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover potential content clusters from unlinked content.
    """
    service = DiscoveryService(db)
    results = await service.discover_content_clusters(
        batch_size=request.batch_size,
        similarity_threshold=request.similarity_threshold
    )
    return SuccessResponse(data=results)
