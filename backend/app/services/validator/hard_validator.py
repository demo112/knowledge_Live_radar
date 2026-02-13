import re
import logging
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseValidator
from app.models.domain_whitelist import DomainWhitelist

logger = logging.getLogger(__name__)

# Common academic paper ID patterns
ARXIV_PATTERN = re.compile(r"\d{4}\.\d{4,5}(v\d+)?")
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


class HardValidator(BaseValidator):
    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        min_length: int = 10,
        banned_words: Optional[List[str]] = None,
        check_url_reachability: bool = True,
        check_whitelist: bool = True,
    ):
        self.db = db
        self.min_length = min_length
        self.banned_words = banned_words or []
        self.check_url_reachability = check_url_reachability
        self.check_whitelist = check_whitelist

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        text = content.get("content", "") or ""
        title = content.get("title", "") or ""
        url = content.get("url", "") or ""

        checks: List[Dict[str, Any]] = []

        # 1. Content length check
        if len(text) < self.min_length and len(title) < self.min_length:
            checks.append({"check": "length", "passed": False, "detail": "Content too short"})
            return False, {"reason": "Content too short", "checks": checks}
        checks.append({"check": "length", "passed": True})

        # 2. Banned words check
        full_text = (title + " " + text).lower()
        for word in self.banned_words:
            pattern = r"\b" + re.escape(word.lower()) + r"\b"
            if re.search(pattern, full_text):
                checks.append({"check": "banned_word", "passed": False, "detail": f"Contains: {word}"})
                return False, {"reason": f"Contains banned word: {word}", "checks": checks}
        checks.append({"check": "banned_word", "passed": True})

        # 3. URL format check
        if url:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                checks.append({"check": "url_format", "passed": False, "detail": "Invalid URL format"})
                return False, {"reason": "Invalid URL format", "checks": checks}
            checks.append({"check": "url_format", "passed": True})

            # 4. Domain whitelist check
            if self.check_whitelist and self.db:
                domain = parsed.netloc.lower()
                # Strip www. prefix
                if domain.startswith("www."):
                    domain = domain[4:]
                wl_result = await self._check_whitelist(domain)
                checks.append(wl_result)
                # Whitelist is advisory — we don't reject, but record credibility
            
            # 5. URL reachability check (lightweight HEAD request)
            if self.check_url_reachability:
                reachable = await self._check_url_reachable(url)
                checks.append(reachable)
                if not reachable["passed"]:
                    return False, {"reason": "URL not reachable", "checks": checks}

        # 6. Paper ID format validation (if content references papers)
        paper_check = self._validate_paper_ids(full_text)
        if paper_check:
            checks.append(paper_check)

        # 7. Date sanity check
        publish_date = content.get("published_at")
        if publish_date:
            date_check = self._validate_date(publish_date)
            checks.append(date_check)
            if not date_check["passed"]:
                return False, {"reason": date_check["detail"], "checks": checks}

        return True, {"reason": "Passed hard validation", "checks": checks}

    async def _check_whitelist(self, domain: str) -> Dict[str, Any]:
        """Check if domain is in whitelist. Returns credibility info."""
        try:
            # Check exact match and wildcard (e.g., *.openai.com)
            result = await self.db.execute(
                select(DomainWhitelist).where(
                    DomainWhitelist.domain.in_([domain, f"*.{domain}"]),
                    DomainWhitelist.is_deleted == False,
                )
            )
            entry = result.scalars().first()

            # Also check parent domain wildcards (e.g., blog.openai.com matches *.openai.com)
            if not entry and "." in domain:
                parent = domain.split(".", 1)[1]
                result = await self.db.execute(
                    select(DomainWhitelist).where(
                        DomainWhitelist.domain == f"*.{parent}",
                        DomainWhitelist.is_deleted == False,
                    )
                )
                entry = result.scalars().first()

            if entry:
                return {
                    "check": "whitelist",
                    "passed": True,
                    "detail": f"Domain '{domain}' in whitelist (credibility: {entry.credibility})",
                    "credibility": entry.credibility,
                }
            return {
                "check": "whitelist",
                "passed": True,  # Not blocking — just informational
                "detail": f"Domain '{domain}' not in whitelist",
                "credibility": 0,
            }
        except Exception as e:
            logger.error(f"Whitelist check error: {e}")
            return {"check": "whitelist", "passed": True, "detail": "Whitelist check skipped (error)"}

    async def _check_url_reachable(self, url: str) -> Dict[str, Any]:
        """Lightweight HEAD request to verify URL is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.head(url)
                if resp.status_code < 400:
                    return {"check": "reachability", "passed": True, "status_code": resp.status_code}
                # Try GET if HEAD fails (some servers don't support HEAD)
                resp = await client.get(url)
                if resp.status_code < 400:
                    return {"check": "reachability", "passed": True, "status_code": resp.status_code}
                return {
                    "check": "reachability",
                    "passed": False,
                    "detail": f"HTTP {resp.status_code}",
                    "status_code": resp.status_code,
                }
        except httpx.TimeoutException:
            return {"check": "reachability", "passed": False, "detail": "Timeout"}
        except Exception as e:
            return {"check": "reachability", "passed": False, "detail": str(e)[:100]}

    def _validate_paper_ids(self, text: str) -> Optional[Dict[str, Any]]:
        """Validate arXiv/DOI IDs if present in text."""
        # Check for arXiv references
        arxiv_refs = re.findall(r"arxiv[:\s]*(\S+)", text, re.IGNORECASE)
        for ref in arxiv_refs:
            if not ARXIV_PATTERN.search(ref):
                return {"check": "paper_id", "passed": False, "detail": f"Invalid arXiv ID: {ref}"}

        # Check for DOI references
        doi_refs = re.findall(r"doi[:\s]*(\S+)", text, re.IGNORECASE)
        for ref in doi_refs:
            if not DOI_PATTERN.search(ref):
                return {"check": "paper_id", "passed": False, "detail": f"Invalid DOI: {ref}"}

        if arxiv_refs or doi_refs:
            return {"check": "paper_id", "passed": True, "detail": "Paper IDs valid"}
        return None  # No paper IDs found, skip check

    def _validate_date(self, date_val) -> Dict[str, Any]:
        """Check date is reasonable (not in far future, not ancient)."""
        from datetime import datetime, timezone, timedelta

        try:
            if isinstance(date_val, str):
                # Try common formats
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
                    try:
                        date_val = datetime.strptime(date_val, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue
                else:
                    return {"check": "date", "passed": True, "detail": "Date format not recognized, skipped"}

            if isinstance(date_val, datetime):
                now = datetime.now(timezone.utc)
                if date_val > now + timedelta(days=2):
                    return {"check": "date", "passed": False, "detail": "Date is in the future"}
                if date_val < datetime(2000, 1, 1, tzinfo=timezone.utc):
                    return {"check": "date", "passed": False, "detail": "Date is unreasonably old"}
                return {"check": "date", "passed": True}

            return {"check": "date", "passed": True, "detail": "Date type not handled, skipped"}
        except Exception:
            return {"check": "date", "passed": True, "detail": "Date validation skipped (error)"}
