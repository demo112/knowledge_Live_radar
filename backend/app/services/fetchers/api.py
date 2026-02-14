import httpx
from typing import List, Dict, Any
from .base import BaseFetcher
import logging

logger = logging.getLogger(__name__)

class APIFetcher(BaseFetcher):
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching API: {url}")
        async with httpx.AsyncClient(headers=self.DEFAULT_HEADERS, follow_redirects=True) as client:
            try:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Error fetching API {url}: {repr(e)}")
                raise

        # Assume API returns a list or a dict with a list field 'items' or 'data'
        items = []
        raw_items = []
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            for key in ['items', 'data', 'posts', 'articles']:
                if key in data and isinstance(data[key], list):
                    raw_items = data[key]
                    break
        
        for item in raw_items:
            # Map common fields
            items.append({
                "title": item.get("title") or item.get("name", ""),
                "url": item.get("url") or item.get("link", ""),
                "content": item.get("content") or item.get("description") or item.get("body", ""),
                "published_at": item.get("published_at") or item.get("created_at"),
                "raw_data": item
            })
        return items

    async def validate_source(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient(headers=self.DEFAULT_HEADERS, follow_redirects=True) as client:
                response = await client.get(url, timeout=15.0)
                return response.status_code == 200
        except Exception:
            return False
