from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auto_discovery import auto_discovery
from app.schemas.common import SuccessResponse
from typing import List

class DiscoveryRequest(BaseModel):
    url: str

class DiscoveryResponse(BaseModel):
    title: str
    url: str
    type: str

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.post("/discover", response_model=SuccessResponse[List[DiscoveryResponse]])
async def discover_sources(request: DiscoveryRequest):
    results = await auto_discovery.discover_from_url(request.url)
    return SuccessResponse(data=results)
