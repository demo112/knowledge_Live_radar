from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.source import InformationSource

class SourceRepository(BaseRepository[InformationSource]):
    def __init__(self, db):
        super().__init__(InformationSource, db)

    async def get_by_url(self, url: str) -> Optional[InformationSource]:
        query = select(InformationSource).where(InformationSource.url == url)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_type(self, type: str) -> List[InformationSource]:
        query = select(InformationSource).where(InformationSource.type == type)
        result = await self.db.execute(query)
        return result.scalars().all()
