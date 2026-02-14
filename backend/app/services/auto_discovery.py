from typing import List, Dict, Any
from bs4 import BeautifulSoup
import httpx
import logging
from urllib.parse import urljoin, urlparse
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.discovered_domain import DiscoveredDomain
from app.services.whitelist_service import WhitelistService

logger = logging.getLogger(__name__)

class SourceDiscoveryService:
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

    async def process_content_links(self, content: str, session: AsyncSession):
        """
        Extract links from content and update DiscoveredDomain.
        """
        if not content:
            return

        # Simple regex for links
        links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
        if not links:
            return

        whitelist_service = WhitelistService(session)
        
        for link in links:
            try:
                # Basic validation
                if len(link) > 500: continue # Skip too long URLs
                
                # Check if it's a valid URL structure
                parsed = urlparse(link)
                if not parsed.netloc: continue
                
                # Record discovery
                domain_record = await whitelist_service.record_discovery(link, has_rss=False)
                
                # Trigger evaluation for this domain
                if domain_record:
                    await self.evaluate_domain(domain_record, session)
                
            except Exception as e:
                logger.debug(f"Error processing link {link}: {e}")

    async def evaluate_domain(self, domain_record: DiscoveredDomain, session: AsyncSession):
        """
        Evaluate if a discovered domain should be a source.
        Includes RSS detection for frequently seen domains.
        """
        whitelist_service = WhitelistService(session)
        is_whitelisted, credibility = await whitelist_service.check_domain(domain_record.domain)
        
        changed = False
        if is_whitelisted:
            if domain_record.evaluation_status != "APPROVED":
                domain_record.evaluation_status = "APPROVED"
                changed = True
        else:
            # If occurrence count is high, mark for manual review
            if domain_record.occurrence_count > 10 and domain_record.evaluation_status == "PENDING":
                domain_record.evaluation_status = "PENDING_REVIEW"
                changed = True
                
            # Proactive RSS detection for frequent domains
            if domain_record.occurrence_count >= 5 and not domain_record.has_rss:
                try:
                    # Construct homepage URL
                    homepage_url = f"https://{domain_record.domain}"
                    feeds = await self.discover_from_url(homepage_url)
                    if feeds:
                        domain_record.has_rss = True
                        changed = True
                        logger.info(f"Detected RSS for discovered domain {domain_record.domain}")
                except Exception as e:
                    logger.debug(f"Failed to detect RSS for {domain_record.domain}: {e}")
        
        if changed:
            session.add(domain_record)
            await session.commit()

source_discovery_service = SourceDiscoveryService()
auto_discovery = source_discovery_service
