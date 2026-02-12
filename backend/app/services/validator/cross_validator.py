from .base import BaseValidator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import ContentItem
from typing import Dict, Any, Tuple

class CrossValidator(BaseValidator):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        url = content.get("url")
        if not url:
            return False, {"reason": "No URL provided"}
            
        stmt = select(ContentItem).where(ContentItem.url == url)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False, {"reason": "Duplicate URL", "existing_id": str(existing.id)}
            
        return True, {"reason": "Unique URL"}
