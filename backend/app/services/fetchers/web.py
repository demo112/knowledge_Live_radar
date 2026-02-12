import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseFetcher

logger = logging.getLogger(__name__)

class WebFetcher(BaseFetcher):
    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string if soup.title else url
                
                # Extract main content - very naive implementation
                # Ideally use readability or similar library
                paragraphs = soup.find_all("p")
                content = "\n".join([p.get_text() for p in paragraphs])
                
                return [{
                    "title": title,
                    "url": url,
                    "content": content,
                    "summary": content[:200] + "..." if len(content) > 200 else content,
                    "publish_time": None, # Hard to extract reliably without metadata
                    "original_id": url
                }]
        except Exception as e:
            logger.error(f"Failed to fetch web content from {url}: {e}")
            raise

    async def validate_source(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code == 200
        except:
            return False
