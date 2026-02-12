import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.api_metric import APIMetric
from app.models.error_record import ErrorRecord

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    async def get_snapshot(self) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            # Last 1 hour metrics
            since = datetime.now() - timedelta(hours=1)
            
            # Avg response time
            stmt = select(func.avg(APIMetric.response_time_ms)).where(APIMetric.created_at >= since)
            avg_resp = await session.scalar(stmt) or 0.0
            
            # Error count
            stmt = select(func.count()).where(ErrorRecord.created_at >= since)
            error_count = await session.scalar(stmt) or 0
            
            return {
                "avg_response_time_ms": avg_resp,
                "error_count_last_hour": error_count,
                "timestamp": str(datetime.now())
            }

    async def get_slow_queries(self, limit: int = 20):
        # Assuming we log slow queries to DB or file.
        # If logged to DB (e.g. as ErrorRecord with type 'slow_query' or specialized table), fetch here.
        # Currently PerformanceTracker logs to logger.
        return []

performance_monitor = PerformanceMonitor()
