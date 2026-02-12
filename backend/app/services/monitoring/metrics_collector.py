import logging
import psutil
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.content import ContentItem, ValidationResult
from app.models.crawl_job import CrawlJob
from app.models.approval import Approval
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

class MetricsCollector:
    async def collect_business_metrics(self) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            # Crawl count today
            today = datetime.now().date()
            stmt = select(func.count()).where(CrawlJob.created_at >= today)
            crawl_count = await session.scalar(stmt) or 0
            
            # Validation pass rate (last 100)
            # Complex query, simplified here
            pass_rate = 0.0 # Placeholder
            
            # Pending approvals
            stmt = select(func.count()).where(Approval.status == "pending")
            pending_approvals = await session.scalar(stmt) or 0
            
            return {
                "crawl_count_today": crawl_count,
                "pass_rate": pass_rate,
                "pending_approvals": pending_approvals
            }

    async def collect_system_metrics(self) -> Dict[str, Any]:
        # CPU/Mem
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used / 1024 / 1024,
            "disk_percent": disk.percent
        }

metrics_collector = MetricsCollector()
