import logging
import uuid
from typing import Optional, List, Tuple
from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_whitelist import DomainWhitelist
from app.models.discovered_domain import DiscoveredDomain

logger = logging.getLogger(__name__)

class WhitelistService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_domain(self, domain: str, credibility: int = 50, reason: Optional[str] = None) -> DomainWhitelist:
        """Add a domain to the whitelist."""
        # Check if exists (including deleted ones)
        stmt = select(DomainWhitelist).where(DomainWhitelist.domain == domain)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.credibility = credibility
            existing.reason = reason
            existing.updated_at = datetime.now()
            if existing.is_deleted:
                existing.is_deleted = False
                logger.info(f"Restored domain to whitelist: {domain}")
            await self.session.commit()
            return existing

        new_domain = DomainWhitelist(
            domain=domain,
            credibility=credibility,
            reason=reason
        )
        self.session.add(new_domain)
        await self.session.commit()
        await self.session.refresh(new_domain)
        logger.info(f"Added domain to whitelist: {domain} (credibility: {credibility})")
        return new_domain

    async def remove_domain(self, domain_id: uuid.UUID) -> bool:
        """Soft delete a domain from whitelist."""
        stmt = select(DomainWhitelist).where(DomainWhitelist.id == domain_id)
        result = await self.session.execute(stmt)
        domain = result.scalar_one_or_none()
        
        if domain:
            domain_name = domain.domain
            domain.is_deleted = True
            domain.updated_at = datetime.now()
            await self.session.commit()
            logger.info(f"Removed domain from whitelist: {domain_name}")
            return True
        return False

    async def check_domain(self, url_or_domain: str) -> Tuple[bool, int]:
        """
        Check if a URL's domain is whitelisted.
        Returns (is_whitelisted, credibility).
        Supports wildcard matching (e.g., *.edu matches mit.edu).
        """
        domain = self._extract_domain(url_or_domain)
        
        # 1. Exact match
        stmt = select(DomainWhitelist).where(DomainWhitelist.domain == domain, DomainWhitelist.is_deleted == False)
        result = await self.session.execute(stmt)
        match = result.scalar_one_or_none()
        
        if match:
            return True, match.credibility

        # 2. Wildcard match (naive implementation for now)
        # Fetch all wildcard domains (start with *.)
        # Ideally this should be cached or optimized
        stmt = select(DomainWhitelist).where(DomainWhitelist.domain.like("%.%"), DomainWhitelist.is_deleted == False)
        result = await self.session.execute(stmt)
        all_domains = result.scalars().all()
        
        for d in all_domains:
            if d.domain.startswith("*."):
                suffix = d.domain[2:]
                if domain.endswith(suffix) or domain == suffix:
                    return True, d.credibility
        
        return False, 0

    async def record_discovery(self, url: str, has_rss: bool = False, source_type: str = "web") -> DiscoveredDomain:
        """Record a discovered domain occurrence."""
        domain = self._extract_domain(url)
        
        stmt = select(DiscoveredDomain).where(DiscoveredDomain.domain == domain)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.occurrence_count += 1
            existing.last_seen_at = datetime.now()
            if has_rss:
                existing.has_rss = True
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            # Check if it's already whitelisted to set initial status
            is_whitelisted, _ = await self.check_domain(domain)
            status = "APPROVED" if is_whitelisted else "PENDING"
            
            new_discovery = DiscoveredDomain(
                domain=domain,
                occurrence_count=1,
                has_rss=has_rss,
                evaluation_status=status
            )
            self.session.add(new_discovery)
            await self.session.commit()
            await self.session.refresh(new_discovery)
            logger.info(f"Recorded new discovered domain: {domain}")
            return new_discovery

    async def get_whitelisted_domains(self, skip: int = 0, limit: int = 100) -> Tuple[List[DomainWhitelist], int]:
        """Get paginated whitelist."""
        stmt = select(DomainWhitelist).where(DomainWhitelist.is_deleted == False).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        
        count_stmt = select(func.count()).select_from(DomainWhitelist).where(DomainWhitelist.is_deleted == False)
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar()
        
        return list(items), total

    async def get_discovered_domains(self, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> Tuple[List[DiscoveredDomain], int]:
        """Get paginated discovered domains."""
        stmt = select(DiscoveredDomain)
        if status:
            stmt = stmt.where(DiscoveredDomain.evaluation_status == status)
        
        stmt = stmt.order_by(DiscoveredDomain.last_seen_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        
        count_stmt = select(func.count()).select_from(DiscoveredDomain)
        if status:
            count_stmt = count_stmt.where(DiscoveredDomain.evaluation_status == status)
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar()
        
        return list(items), total

    def _extract_domain(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            return url
        try:
            return urlparse(url).netloc
        except:
            return url
