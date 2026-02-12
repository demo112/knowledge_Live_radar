from fastapi import APIRouter
from app.services.monitoring import performance_monitor, metrics_collector

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/snapshot")
async def get_snapshot():
    return await performance_monitor.get_snapshot()

@router.get("/business-metrics")
async def get_business_metrics():
    return await metrics_collector.collect_business_metrics()

@router.get("/system-metrics")
async def get_system_metrics():
    return await metrics_collector.collect_system_metrics()
