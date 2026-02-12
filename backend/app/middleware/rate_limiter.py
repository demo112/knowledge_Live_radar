import time
import logging
from typing import Tuple
from app.services.cache import cache_service
from app.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    # Default limits
    DEFAULT_LIMITS = {
        "default": {"requests": 60, "window_seconds": 60},
        "ai": {"requests": 10, "window_seconds": 60},
        "export": {"requests": 5, "window_seconds": 300},
    }
    
    def __init__(self):
        self.cache_service = cache_service
    
    async def check_rate_limit(self, client_ip: str, endpoint_category: str = "default") -> Tuple[bool, int]:
        """
        Check rate limit for IP and category.
        Returns (is_allowed, remaining_seconds)
        """
        limit_config = self.DEFAULT_LIMITS.get(endpoint_category, self.DEFAULT_LIMITS["default"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window_seconds"]
        
        # Key format: rate_limit:{category}:{ip}:{window_start_timestamp}
        # Using a sliding window approximation or fixed window for simplicity.
        # Here we use fixed window based on time block.
        current_window = int(time.time() / window_seconds)
        key = f"rate_limit:{endpoint_category}:{client_ip}:{current_window}"
        
        try:
            # Increment request count
            current_count = await self.cache_service.get(key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            if current_count >= max_requests:
                # Calculate time until next window
                next_window_start = (current_window + 1) * window_seconds
                remaining_seconds = max(0, int(next_window_start - time.time()))
                return False, remaining_seconds
            
            await self.cache_service.set(key, current_count + 1, ttl=window_seconds)
            return True, 0
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open if cache error
            return True, 0

    async def record_request(self, client_ip: str, endpoint_category: str) -> None:
        """Record request (already handled in check_rate_limit logic above)"""
        pass

rate_limiter = RateLimiter()
