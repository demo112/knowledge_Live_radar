import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseFetcher
from .request_utils import RequestUtils, RateLimitException

logger = logging.getLogger(__name__)

class WebFetcher(BaseFetcher):
    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        try:
            # 使用 RequestUtils 进行拟人化请求
            response = await RequestUtils.fetch_url(url)
            
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
        except RateLimitException as e:
            logger.warning(f"Rate limited for {url}: {e}")
            raise
        except Exception as e:
                logger.error(f"Failed to fetch web content from {url}: {repr(e)}")
                raise

    async def validate_source(self, url: str) -> bool:
        try:
            # Try HEAD first
            try:
                await RequestUtils.fetch_url(url, method="HEAD", timeout=10.0)
                return True
            except Exception:
                pass
            
            # Fallback to GET
            await RequestUtils.fetch_url(url, method="GET", timeout=15.0)
            return True
        except Exception:
            return False
