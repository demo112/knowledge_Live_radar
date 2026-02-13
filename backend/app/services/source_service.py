from uuid import UUID
from typing import List, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.source import SourceRepository
from app.schemas.source import SourceCreate, SourceUpdate

class SourceService:
    def __init__(self, db: AsyncSession):
        self.source_repo = SourceRepository(db)
        self.db = db

    async def create_source(self, schema: SourceCreate) -> Any:
        # Check if URL exists
        existing = await self.source_repo.get_by_url(schema.url)
        if existing:
            raise HTTPException(status_code=400, detail="该 URL 的信息源已存在")
        
        return await self.source_repo.create(schema.model_dump())

    async def get_source(self, id: UUID) -> Any:
        source = await self.source_repo.get(id)
        if not source:
            raise HTTPException(status_code=404, detail="未找到信息源")
        return source

    async def get_all_sources(self, skip: int = 0, limit: int = 100) -> List[Any]:
        return await self.source_repo.get_all(skip, limit)

    async def update_source(self, id: UUID, schema: SourceUpdate) -> Any:
        source = await self.get_source(id)
        return await self.source_repo.update(source, schema.model_dump(exclude_unset=True))

    async def delete_source(self, id: UUID) -> Any:
        await self.get_source(id)
        return await self.source_repo.soft_delete(id)
