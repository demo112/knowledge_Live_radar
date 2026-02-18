from typing import List, Dict, Any
import logging
from datetime import datetime
from firecrawl import FirecrawlApp
from app.services.fetchers.base import BaseFetcher
from app.config import settings
import asyncio

logger = logging.getLogger(__name__)

class FirecrawlFetcher(BaseFetcher):
    def __init__(self):
        self.app = FirecrawlApp(
            api_key=settings.FIRECRAWL_API_KEY,
            api_url=settings.FIRECRAWL_API_URL
        )

    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch content using Firecrawl.
        For a single URL, it returns a list with one item.
        For crawl, it returns multiple items.
        """
        logger.info(f"Fetching via Firecrawl: {url}")
        
        # Determine if scrape or crawl
        # For now, let's assume 'scrape' for single page
        try:
            # Run synchronous scrape in thread pool
            # v1.0.0+ uses .scrape(url, only_main_content=True)
            # All params must be kwargs
            result = await asyncio.to_thread(
                self.app.scrape, 
                url, 
                only_main_content=True
            )
            
            # Handle result (Object or Dict)
            if hasattr(result, 'markdown'):
                markdown = result.markdown
                metadata = result.metadata if hasattr(result, 'metadata') else {}
                source_url = metadata.get('sourceURL') if isinstance(metadata, dict) else getattr(metadata, 'sourceURL', url)
                title = metadata.get('title') if isinstance(metadata, dict) else getattr(metadata, 'title', 'Untitled')
                description = metadata.get('description') if isinstance(metadata, dict) else getattr(metadata, 'description', None)
                original_data = result.model_dump() if hasattr(result, 'model_dump') else result.__dict__
            elif isinstance(result, dict):
                # Fallback for dict response
                if 'data' in result:
                    result = result['data']
                markdown = result.get('markdown')
                metadata = result.get('metadata', {})
                source_url = metadata.get('sourceURL', url)
                title = metadata.get('title', 'Untitled')
                description = metadata.get('description')
                original_data = result
            else:
                logger.warning(f"Firecrawl returned unknown type for {url}: {type(result)}")
                return []
            
            if not markdown:
                logger.warning(f"Firecrawl returned no markdown for {url}")
                return []

            content_item = {
                "title": title or "Untitled",
                "url": source_url or url,
                "content": markdown,
                "summary": description,
                "published_at": datetime.now(), # Firecrawl doesn't always return publish date
                "original_data": original_data
            }
            return [content_item]
            
        except Exception as e:
            logger.error(f"Firecrawl fetch error: {e}")
            raise

    async def validate_source(self, url: str) -> bool:
        try:
            # Simple scrape to validate
            await self.fetch(url)
            return True
        except Exception as e:
            logger.error(f"Firecrawl validation failed for {url}: {e}")
            return False
