from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.hotspot import Hotspot
from app.schemas.health import HotspotSchema
from app.services.evolution.hotspot_manager import HotspotManager

router = APIRouter(
    prefix="/hotspots",
    tags=["hotspots"]
)

@router.get("/", response_model=List[HotspotSchema])
async def list_hotspots(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List hotspots with optional status filtering.
    """
    query = select(Hotspot).order_by(desc(Hotspot.heat_score)).offset(offset).limit(limit)
    
    if status:
        query = query.where(Hotspot.status == status)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{id}", response_model=HotspotSchema)
async def get_hotspot(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get hotspot details.
    """
    result = await db.execute(select(Hotspot).where(Hotspot.id == id))
    hotspot = result.scalars().first()
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return hotspot

@router.put("/{id}/status")
async def update_hotspot_status(
    id: uuid.UUID,
    status: str = Query(..., regex="^(new|emerging|trending|mature|cooling|archived)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually update hotspot status.
    """
    result = await db.execute(select(Hotspot).where(Hotspot.id == id))
    hotspot = result.scalars().first()
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
        
    hotspot.status = status
    await db.commit()
    await db.refresh(hotspot)
    return hotspot

@router.post("/lifecycle/update")
async def trigger_lifecycle_update(
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger manual update of hotspot lifecycle (usually scheduled).
    """
    manager = HotspotManager(db)
    await manager.update_lifecycle()
    return {"status": "success", "message": "Lifecycle update triggered"}
