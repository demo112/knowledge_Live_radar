import time
import logging
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.database import AsyncSessionLocal
from app.models.api_metric import APIMetric

logger = logging.getLogger(__name__)

class PerformanceTrackerMiddleware(BaseHTTPMiddleware):
    SLOW_QUERY_THRESHOLD_MS = 3000
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = (time.time() - start_time) * 1000
            
            # Log slow queries
            if process_time > self.SLOW_QUERY_THRESHOLD_MS:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}ms")
            
            # Record metric asynchronously
            asyncio.create_task(self.record_metric(request.url.path, request.method, status_code, process_time))
            
    async def record_metric(self, endpoint: str, method: str, status_code: int, process_time: float):
        try:
            async with AsyncSessionLocal() as session:
                metric = APIMetric(
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    response_time_ms=process_time
                )
                session.add(metric)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
