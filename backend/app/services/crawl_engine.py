from typing import List, Dict, Any
from app.services.fetchers import get_fetcher
from app.models.source import InformationSource
import logging

logger = logging.getLogger(__name__)

class CrawlEngine:
    async def crawl_source(self, source: InformationSource) -> List[Dict[str, Any]]:
        """
        Crawl a single source.
        """
        logger.info(f"Starting crawl for source: {source.name} ({source.type})")
        
        try:
            fetcher = get_fetcher(source.type)
            items = await fetcher.fetch(source.url)
            logger.info(f"Fetched {len(items)} items from {source.name}")
            return items
        except Exception as e:
            logger.error(f"Failed to crawl source {source.name}: {e}")
            raise

    async def validate_source(self, type: str, url: str) -> bool:
        try:
            fetcher = get_fetcher(type)
            return await fetcher.validate_source(url)
        except Exception as e:
            logger.error(f"Validation failed for {url}: {e}")
            return False

crawl_engine = CrawlEngine()
