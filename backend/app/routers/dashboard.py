from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.database import get_db
from app.models.source import InformationSource
from app.models.discovered_domain import DiscoveredDomain
from app.models.domain_whitelist import DomainWhitelist
from app.models.content import ContentItem, ValidationResult
from app.schemas.dashboard import DashboardStats, DashboardTrend, DailyTrend

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

@router.get("/trend", response_model=DashboardTrend)
async def get_dashboard_trend(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    # Calculate start date
    start_date = datetime.now() - timedelta(days=days)
    
    # Query validation results
    stmt = select(ValidationResult.verified_at, ValidationResult.overall_score).where(
        ValidationResult.verified_at >= start_date
    ).order_by(ValidationResult.verified_at)
    
    results = (await db.execute(stmt)).all()
    
    # Group by date in python
    daily_data = {}
    for verified_at, score in results:
        if not verified_at:
            continue
        date_str = verified_at.strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {"total": 0, "passed": 0}
        
        daily_data[date_str]["total"] += 1
        if score is not None and score >= 60:
            daily_data[date_str]["passed"] += 1
            
    # Format response
    trends = []
    # Ensure all days are covered
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
        data = daily_data.get(date, {"total": 0, "passed": 0})
        pass_rate = 0.0
        if data["total"] > 0:
            pass_rate = (data["passed"] / data["total"]) * 100
            
        trends.append(DailyTrend(
            date=date,
            total_validations=data["total"],
            pass_rate=round(pass_rate, 2)
        ))
        
    return DashboardTrend(trends=trends)
