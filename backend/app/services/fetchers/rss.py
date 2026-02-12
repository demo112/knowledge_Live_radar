import feedparser
import httpx
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseFetcher
import logging
from time import mktime

logger = logging.getLogger(__name__)

class RSSFetcher(BaseFetcher):
    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching RSS feed: {url}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                content = response.text
            except Exception as e:
                logger.error(f"Error fetching RSS feed {url}: {e}")
                raise

        feed = feedparser.parse(content)
        items = []
        for entry in feed.entries:
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))
            
            items.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "content": entry.get("summary", "") or entry.get("description", ""),
                "published_at": published_at,
                "author": entry.get("author", ""),
                "tags": [tag.term for tag in entry.get("tags", [])]
            })
        return items

    async def validate_source(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                if response.status_code != 200:
                    return False
                feed = feedparser.parse(response.text)
                return bool(feed.version)
        except Exception:
            return False
