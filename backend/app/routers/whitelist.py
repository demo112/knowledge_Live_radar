from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.whitelist_service import WhitelistService
from app.schemas.whitelist import (
    DomainWhitelistCreate, 
    DomainWhitelistResponse, 
    PaginatedWhitelist, 
    PaginatedDiscovered,
    DiscoveredDomainResponse,
    DomainCheckRequest
)

router = APIRouter(prefix="/whitelist", tags=["whitelist"])

@router.post("/", response_model=DomainWhitelistResponse)
async def add_domain(
    item: DomainWhitelistCreate,
    db: AsyncSession = Depends(get_db)
):
    service = WhitelistService(db)
    return await service.add_domain(item.domain, item.credibility, item.reason)

@router.get("/", response_model=PaginatedWhitelist)
async def get_whitelist(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = WhitelistService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_whitelisted_domains(skip, page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.delete("/{domain_id}")
async def remove_domain(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = WhitelistService(db)
    success = await service.remove_domain(domain_id)
    if not success:
        raise HTTPException(status_code=404, detail="未找到域名")
    return {"success": True}

@router.get("/discovered", response_model=PaginatedDiscovered)
async def get_discovered_domains(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = WhitelistService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_discovered_domains(status, skip, page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/check")
async def check_domain(
    item: DomainCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    service = WhitelistService(db)
    is_whitelisted, credibility = await service.check_domain(item.url)
    return {
        "is_whitelisted": is_whitelisted,
        "credibility": credibility
    }
