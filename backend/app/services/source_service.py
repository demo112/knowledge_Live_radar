from uuid import UUID
from typing import List, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.source import SourceRepository
from app.schemas.source import SourceCreate, SourceUpdate
from app.services.fetchers.wechat_utils import extract_wechat_info

class SourceService:
    def __init__(self, db: AsyncSession):
        self.source_repo = SourceRepository(db)
        self.db = db

    async def create_source(self, schema: SourceCreate) -> Any:
        # Special handling for WeChat Official Accounts
        if schema.type == "WECHAT_MP":
            # Check if input looks like a URL
            if "mp.weixin.qq.com/s" in schema.url:
                try:
                    info = await extract_wechat_info(schema.url)
                    if info:
                        # Use nickname or user_name as the identifier for RSSHub
                        identifier = info.get("nickname") or info.get("user_name")
                        if identifier:
                            schema.url = identifier
                            # Update name if it looks like a placeholder
                            if not schema.name or schema.name == "New Source" or "http" in schema.name:
                                schema.name = info.get("nickname", identifier)
                        else:
                            raise ValueError("Extraction returned empty info")
                    else:
                        raise ValueError("Extraction failed")
                except Exception:
                    raise HTTPException(
                        status_code=400, 
                        detail="无法自动从文章链接提取公众号信息（可能是因为反爬虫限制）。请直接在 URL 字段输入公众号名称（如 '机器之心'）或微信号 ID。"
                    )
            else:
                # Assume the input is already a nickname or ID
                pass

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
