from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.source import InformationSource
from app.models.discovered_domain import DiscoveredDomain
from app.models.domain_whitelist import DomainWhitelist
from app.models.content import ContentItem, ValidationResult
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    # Sources
    stmt_sources = select(func.count()).select_from(InformationSource).where(InformationSource.is_deleted == False)
    total_sources = (await db.execute(stmt_sources)).scalar() or 0
    
    stmt_active = select(func.count()).select_from(InformationSource).where(
        and_(InformationSource.is_deleted == False, InformationSource.status == "ACTIVE")
    )
    active_sources = (await db.execute(stmt_active)).scalar() or 0
    
    # Discovered Domains
    stmt_discovered = select(func.count()).select_from(DiscoveredDomain)
    discovered_domains = (await db.execute(stmt_discovered)).scalar() or 0
    
    # Whitelist
    stmt_whitelist = select(func.count()).select_from(DomainWhitelist).where(DomainWhitelist.is_deleted == False)
    whitelisted_domains = (await db.execute(stmt_whitelist)).scalar() or 0
    
    # Contents
    stmt_contents = select(func.count()).select_from(ContentItem).where(ContentItem.is_deleted == False)
    total_contents = (await db.execute(stmt_contents)).scalar() or 0
    
    # Validation Rate
    # Assuming overall_score >= 60 is passed
    # Check if overall_score exists in ValidationResult
    # ValidationResult is joined with ContentItem usually, but here we just query table
    
    stmt_validations = select(func.count()).select_from(ValidationResult)
    total_validations = (await db.execute(stmt_validations)).scalar() or 0
    
    pass_rate = 0.0
    if total_validations > 0:
        stmt_passed = select(func.count()).select_from(ValidationResult).where(ValidationResult.overall_score >= 60)
        passed = (await db.execute(stmt_passed)).scalar() or 0
        pass_rate = (passed / total_validations) * 100
        
    return DashboardStats(
        total_sources=total_sources,
        active_sources=active_sources,
        discovered_domains=discovered_domains,
        whitelisted_domains=whitelisted_domains,
        total_contents=total_contents,
        validation_pass_rate=round(pass_rate, 2)
    )
