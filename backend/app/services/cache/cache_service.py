import json
import logging
import fnmatch
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    # TTL Constants
    PYRAMID_CACHE_TTL = 300      # 5 minutes
    SEARCH_CACHE_TTL = 60        # 1 minute
    METRICS_CACHE_TTL = 30       # 30 seconds
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        self.memory_cache = {} # Fallback for dev/testing if Redis fails or not configured
        self._use_redis = False
        
    async def initialize(self):
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                self._use_redis = True
                logger.info(f"Connected to Redis at {self.redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                self._use_redis = False
        else:
            logger.info("No REDIS_URL configured. Using in-memory cache.")
            
    async def get(self, key: str) -> Optional[Any]:
        if self._use_redis and self.redis_client:
            try:
                val = await self.redis_client.get(key)
                if val:
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return val
                return None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return self.memory_cache.get(key)
        else:
            return self.memory_cache.get(key)
            
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if isinstance(value, (dict, list)):
            str_value = json.dumps(value)
        else:
            str_value = str(value)
            
        if self._use_redis and self.redis_client:
            try:
                await self.redis_client.set(key, str_value, ex=ttl)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                self.memory_cache[key] = value # Fallback
        else:
            self.memory_cache[key] = value
            
    async def delete(self, key: str) -> None:
        if self._use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if key in self.memory_cache:
            del self.memory_cache[key]
            
    async def delete_pattern(self, pattern: str) -> int:
        count = 0
        if self._use_redis and self.redis_client:
            try:
                keys = []
                # redis scan_iter uses glob style patterns
                async for key in self.redis_client.scan_iter(pattern):
                    keys.append(key)
                if keys:
                    count = await self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis delete_pattern error: {e}")
        
        # In-memory pattern delete
        keys_to_delete = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
        for k in keys_to_delete:
            del self.memory_cache[k]
            if not self._use_redis: # Count only if not counted by redis
                count += 1
        return count

    def _match_pattern(self, key: str, pattern: str) -> bool:
        return fnmatch.fnmatch(key, pattern)

    async def invalidate_pyramid(self, pyramid_id: str) -> None:
        """Invalidate pyramid related cache"""
        await self.delete_pattern(f"pyramid:{pyramid_id}*")
        
    async def invalidate_search(self) -> None:
        """Invalidate search cache"""
        await self.delete_pattern("search:*")
        
    async def close(self):
        if self.redis_client:
            await self.redis_client.close()

# Global instance
cache_service = CacheService()
