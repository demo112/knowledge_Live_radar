from .base import BaseValidator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.content import ContentItem
from app.services.ai_service import ai_service
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)

class CrossValidator(BaseValidator):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Cross-validation: URL dedup + multi-source topic confirmation.
        
        Returns (is_unique, details) where details includes:
        - dedup check result
        - cross-source confirmation count
        - consistency analysis (if similar content found)
        """
        url = content.get("url")
        title = content.get("title", "")
        
        if not url:
            return False, {"reason": "No URL provided"}

        # Step 1: URL deduplication
        stmt = select(ContentItem).where(ContentItem.url == url)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False, {
                "reason": "Duplicate URL",
                "existing_id": str(existing.id),
                "cross_source_count": 0,
                "verification_status": "duplicate",
            }

        # Step 2: Find similar content by title (multi-source confirmation)
        similar_items = await self._find_similar_content(title)
        cross_source_count = len(similar_items)
        
        details = {
            "reason": "Unique URL",
            "cross_source_count": cross_source_count,
            "verification_status": "single_source",
        }

        if cross_source_count > 0:
            # Step 3: AI consistency check with existing similar content
            consistency = await self._check_consistency(content, similar_items)
            details["verification_status"] = consistency.get("status", "single_source")
            details["consistency_score"] = consistency.get("score", 0)
            details["conflicts"] = consistency.get("conflicts", [])
            
            if consistency.get("status") == "confirmed":
                details["reason"] = f"Multi-source confirmed ({cross_source_count} similar sources)"
            elif consistency.get("status") == "conflict":
                details["reason"] = f"Conflict detected with {cross_source_count} existing sources"

        return True, details

    async def _find_similar_content(self, title: str, limit: int = 5) -> List[ContentItem]:
        """Find content with similar titles (potential multi-source coverage)."""
        if not title or len(title) < 5:
            return []

        # Extract key words from title (simple approach: words > 3 chars)
        words = [w for w in title.split() if len(w) > 3]
        if not words:
            return []

        # Search by the longest/most distinctive words (up to 3)
        search_words = sorted(words, key=len, reverse=True)[:3]
        
        conditions = []
        for word in search_words:
            conditions.append(ContentItem.title.ilike(f"%{word}%"))

        if not conditions:
            return []

        # Require at least 2 words to match (if we have 2+), otherwise 1
        min_matches = min(2, len(conditions))
        
        # Simple approach: OR match then filter in memory
        stmt = (
            select(ContentItem)
            .where(or_(*conditions))
            .order_by(ContentItem.created_at.desc())
            .limit(limit * 3)  # Fetch more, filter later
        )
        result = await self.session.execute(stmt)
        candidates = result.scalars().all()

        # Filter: count how many search words appear in each candidate's title
        similar = []
        for item in candidates:
            item_title_lower = (item.title or "").lower()
            match_count = sum(1 for w in search_words if w.lower() in item_title_lower)
            if match_count >= min_matches:
                similar.append(item)
                if len(similar) >= limit:
                    break

        return similar

    async def _check_consistency(self, new_content: Dict[str, Any], existing: List[ContentItem]) -> Dict[str, Any]:
        """Use AI to check if new content is consistent with existing similar content."""
        if not ai_service.client or not existing:
            return {"status": "single_source", "score": 0, "conflicts": []}

        new_title = new_content.get("title", "")
        new_text = (new_content.get("content", "") or "")[:1000]
        
        existing_summaries = []
        for item in existing[:3]:  # Compare with up to 3 existing items
            summary = item.summary or item.title or ""
            source_id = str(item.source_id) if item.source_id else "unknown"
            existing_summaries.append(f"[Source {source_id}] {item.title}: {summary[:200]}")

        existing_text = "\n".join(existing_summaries)

        prompt = f"""Compare the following new content with existing content on a similar topic.

New Content:
Title: {new_title}
Text: {new_text[:500]}

Existing Similar Content:
{existing_text}

Determine:
1. Are they about the same topic? (yes/no)
2. Is the information consistent? (score 0-100)
3. Any conflicts? (list briefly in Chinese)

Return JSON:
{{"same_topic": true/false, "consistency": 0-100, "conflicts": ["..."], "status": "confirmed/conflict/unrelated"}}"""

        try:
            response = await ai_service.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a fact-checking assistant. Return only valid JSON. Ensure all text content in JSON is in Chinese."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            if response:
                parsed = ai_service._parse_json(response)
                return {
                    "status": parsed.get("status", "single_source"),
                    "score": parsed.get("consistency", 0),
                    "conflicts": parsed.get("conflicts", []),
                }
        except Exception as e:
            logger.error(f"Cross-validation AI check failed: {e}")

        return {"status": "single_source", "score": 0, "conflicts": []}
