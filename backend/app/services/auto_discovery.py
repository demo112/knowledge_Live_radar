from typing import List, Dict, Any
from bs4 import BeautifulSoup
import httpx
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class AutoDiscovery:
    async def discover_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Discover potential sources from a URL.
        Returns list of {title, url, type}.
        """
        logger.info(f"Discovering sources from {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True, timeout=10.0)
                response.raise_for_status()
                html = response.text
                
            soup = BeautifulSoup(html, 'html.parser')
            discovered = []
            
            # Find RSS/Atom feeds
            for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    title = link.get('title') or "RSS Feed"
                    discovered.append({
                        "title": title,
                        "url": full_url,
                        "type": "rss"
                    })
            
            # Find links that look like feeds (heuristic)
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and ('rss' in href.lower() or 'feed' in href.lower() or 'atom' in href.lower()):
                     full_url = urljoin(url, href)
                     # Avoid duplicates
                     if not any(d['url'] == full_url for d in discovered):
                        discovered.append({
                            "title": a.get_text().strip() or "Potential Feed",
                            "url": full_url,
                            "type": "rss"
                        })

            logger.info(f"Discovered {len(discovered)} sources")
            return discovered
            
        except Exception as e:
            logger.error(f"Auto discovery failed for {url}: {e}")
            return []

auto_discovery = AutoDiscovery()
