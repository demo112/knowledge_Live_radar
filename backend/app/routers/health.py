import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.health_report import HealthReport, HealthReportType
from app.schemas.health import HealthReportSchema

from app.services.evolution.health_detector import HealthDetector
from app.services.evolution.restructure_advisor import RestructureAdvisor

router = APIRouter(prefix="/health", tags=["health"])

@router.post("/detect", response_model=dict)
async def trigger_health_detection(
    type: HealthReportType = HealthReportType.MANUAL,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a full system health detection.
    """
    detector = HealthDetector(db)
    report = await detector.run_full_detection(report_type=type)
    return {"success": True, "report_id": str(report.id), "overall_score": report.overall_score}

@router.get("/report/latest", response_model=HealthReportSchema)
async def get_latest_health_report(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HealthReport).order_by(HealthReport.created_at.desc()).limit(1)
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="No health report found")
    return report

@router.post("/evolution/restructure", response_model=dict)
async def trigger_restructure_analysis(
    pyramid_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger restructure analysis (moved back here for compatibility/completeness).
    """
    advisor = RestructureAdvisor(db)
    proposals = await advisor.analyze_and_propose(pyramid_id)
    return {"success": True, "proposals_generated": len(proposals)}
