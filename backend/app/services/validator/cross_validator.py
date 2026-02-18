from .base import BaseValidator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.content import ContentItem
from app.core.ai.client import ai_client
from app.core.ai.facade import ai_facade
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)

class CrossValidator(BaseValidator):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        交叉验证：URL 去重 + 多源话题确认。
        
        返回 (is_unique, details)，其中 details 包含：
        - 去重检查结果
        - 跨源确认数量
        - 一致性分析（如果找到相似内容）
        """
        url = content.get("url")
        title = content.get("title", "")
        
        if not url:
            return False, {"reason": "No URL provided"}

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

        similar_items = await self._find_similar_content(title)
        cross_source_count = len(similar_items)
        
        details = {
            "reason": "Unique URL",
            "cross_source_count": cross_source_count,
            "verification_status": "single_source",
        }

        if cross_source_count > 0:
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
        if not title or len(title) < 5:
            return []

        words = [w for w in title.split() if len(w) > 3]
        if not words:
            return []

        search_words = sorted(words, key=len, reverse=True)[:3]
        
        conditions = []
        for word in search_words:
            conditions.append(ContentItem.title.ilike(f"%{word}%"))

        if not conditions:
            return []

        min_matches = min(2, len(conditions))
        
        stmt = (
            select(ContentItem)
            .where(or_(*conditions))
            .order_by(ContentItem.created_at.desc())
            .limit(limit * 3)
        )
        result = await self.session.execute(stmt)
        candidates = result.scalars().all()

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
        if not existing:
            return {"status": "single_source", "score": 0, "conflicts": []}

        new_title = new_content.get("title", "")
        new_text = (new_content.get("content", "") or "")[:1000]
        
        existing_summaries = []
        for item in existing[:3]:
            summary = item.summary or item.title or ""
            source_id = str(item.source_id) if item.source_id else "unknown"
            existing_summaries.append(f"[Source {source_id}] {item.title}: {summary[:200]}")

        existing_text = "\n".join(existing_summaries)

        try:
            result = await ai_facade.check_consistency(
                new_title=new_title,
                new_text=new_text,
                existing_content=existing_text
            )
            return result
        except Exception as e:
            logger.error(f"Cross-validation AI check failed: {e}")

        return {"status": "single_source", "score": 0, "conflicts": []}
