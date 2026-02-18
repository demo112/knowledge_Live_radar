from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, desc, and_, case
from app.models.ai_metric import AIMetric
import logging

logger = logging.getLogger(__name__)

class AIMonitorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_metrics(
        self, 
        skip: int = 0, 
        limit: int = 50, 
        module: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> tuple[List[AIMetric], int]:
        """
        Get paginated metrics with optional filters.
        Returns (items, total_count)
        """
        query = select(AIMetric)
        count_query = select(func.count()).select_from(AIMetric)
        
        conditions = []
        if module:
            conditions.append(AIMetric.module == module)
        if model:
            conditions.append(AIMetric.model == model)
        if provider:
            conditions.append(AIMetric.provider == provider)
        if status:
            conditions.append(AIMetric.status == status)
        if start_time:
            conditions.append(AIMetric.timestamp >= start_time)
        if end_time:
            conditions.append(AIMetric.timestamp <= end_time)
            
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
            
        # Get total count
        total = await self.db.scalar(count_query) or 0
        
        # Get items
        query = query.order_by(desc(AIMetric.timestamp)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total

    async def get_aggregated_stats(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get aggregated stats by model and provider.
        """
        conditions = []
        if start_time:
            conditions.append(AIMetric.timestamp >= start_time)
        if end_time:
            conditions.append(AIMetric.timestamp <= end_time)
            
        # Overall stats
        overall_query = select(
            func.count(AIMetric.id).label("total_requests"),
            func.sum(case((AIMetric.status == "success", 1), else_=0)).label("successful_requests"),
            func.sum(AIMetric.total_tokens).label("total_tokens"),
            func.avg(AIMetric.latency).label("avg_latency")
        )
        
        if conditions:
            overall_query = overall_query.where(and_(*conditions))
            
        overall_result = await self.db.execute(overall_query)
        overall_row = overall_result.one()
        
        total_requests = overall_row.total_requests or 0
        successful_requests = overall_row.successful_requests or 0
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        total_tokens = overall_row.total_tokens or 0
        avg_latency = overall_row.avg_latency or 0.0
        
        # Stats by model
        model_query = select(
            AIMetric.model,
            func.count(AIMetric.id).label("count"),
            func.avg(AIMetric.latency).label("avg_latency"),
            func.sum(AIMetric.total_tokens).label("total_tokens"),
            func.sum(case((AIMetric.status == "success", 1), else_=0)).label("success_count")
        ).group_by(AIMetric.model)
        
        if conditions:
            model_query = model_query.where(and_(*conditions))
            
        model_result = await self.db.execute(model_query)
        model_stats = []
        for row in model_result:
            count = row.count
            success_count = row.success_count
            rate = (success_count / count * 100) if count > 0 else 0
            model_stats.append({
                "model": row.model,
                "count": count,
                "avg_latency": row.avg_latency or 0.0,
                "total_tokens": row.total_tokens or 0,
                "success_rate": rate
            })
            
        return {
            "total_requests": total_requests,
            "success_rate": success_rate,
            "total_tokens": total_tokens,
            "avg_latency": avg_latency,
            "models": model_stats
        }

    async def clean_old_metrics(self, days: int = 30) -> int:
        """
        Delete metrics older than N days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        query = delete(AIMetric).where(AIMetric.timestamp < cutoff_date)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount
