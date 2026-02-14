import httpx
import logging
import random
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RateLimitException(Exception):
    """Raised when 429 or 403 is encountered."""
    pass

class RequestUtils:
    # 常用浏览器 UA 池
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    @classmethod
    def get_random_headers(cls, referer: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        if referer:
            headers["Referer"] = referer
            headers["Sec-Fetch-Site"] = "same-origin"
        return headers

    @classmethod
    async def random_sleep(cls, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Pre-request random delay to mimic human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sniffing delay: {delay:.2f}s")
        await asyncio.sleep(delay)

    @classmethod
    @asynccontextmanager
    async def smart_client(cls, referer: Optional[str] = None, timeout: float = 30.0):
        """
        Context manager providing a configured httpx.AsyncClient.
        Usage:
            async with RequestUtils.smart_client() as client:
                resp = await client.get(url)
        """
        headers = cls.get_random_headers(referer)
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
            yield client

    @classmethod
    async def fetch_url(cls, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        """
        High-level fetch with sniffing strategy (delay + random UA + error handling).
        """
        # 1. Random delay before request
        await cls.random_sleep()

        # 2. Prepare headers
        headers = cls.get_random_headers(kwargs.get("referer"))
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        timeout = kwargs.pop("timeout", 30.0)

        # 3. Execute request
        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, **kwargs)
                elif method.upper() == "HEAD":
                    response = await client.head(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                # 4. Check for blocking
                if response.status_code in [403, 429]:
                    logger.warning(f"Access denied ({response.status_code}) for {url}")
                    raise RateLimitException(f"Blocked with status {response.status_code}")
                
                response.raise_for_status()
                return response

        except httpx.HTTPStatusError as e:
            if e.response.status_code in [403, 429]:
                raise RateLimitException(f"Blocked with status {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise
