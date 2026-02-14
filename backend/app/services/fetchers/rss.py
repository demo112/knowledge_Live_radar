import feedparser
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseFetcher
import logging
from time import mktime
from .request_utils import RequestUtils, RateLimitException

logger = logging.getLogger(__name__)

class RSSFetcher(BaseFetcher):
    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        logger.info(f"Sniffing RSS feed: {url}")
        try:
            # 使用 RequestUtils 进行拟人化请求
            response = await RequestUtils.fetch_url(url)
            content = response.text
        except RateLimitException as e:
            logger.warning(f"Rate limited for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching RSS feed {url}: {repr(e)}")
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
            # 验证时也使用拟人化请求
            response = await RequestUtils.fetch_url(url, timeout=15.0)
            feed = feedparser.parse(response.text)
            return bool(feed.version)
        except Exception:
            return False
