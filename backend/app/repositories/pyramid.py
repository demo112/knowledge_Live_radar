from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.pyramid import Pyramid, PyramidNode

class PyramidRepository(BaseRepository[Pyramid]):
    def __init__(self, db):
        super().__init__(Pyramid, db)

    async def get_with_nodes(self, id: UUID) -> Optional[Pyramid]:
        query = select(Pyramid).options(selectinload(Pyramid.nodes)).where(Pyramid.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class PyramidNodeRepository(BaseRepository[PyramidNode]):
    def __init__(self, db):
        super().__init__(PyramidNode, db)
    
    async def get_by_pyramid(self, pyramid_id: UUID) -> List[PyramidNode]:
        query = select(PyramidNode).where(PyramidNode.pyramid_id == pyramid_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_children(self, parent_id: UUID) -> List[PyramidNode]:
        query = select(PyramidNode).where(PyramidNode.parent_id == parent_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_descendants_path(self, pyramid_id: UUID, old_prefix: str, new_prefix: str, level_diff: int):
        query = (
            update(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .where(PyramidNode.path.like(f"{old_prefix}%"))
            .values(
                path=func.replace(PyramidNode.path, old_prefix, new_prefix),
                level=PyramidNode.level + level_diff
            )
        )
        await self.db.execute(query)

    async def soft_delete_by_pyramid(self, pyramid_id: UUID):
        query = (
            update(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .values(is_deleted=True)
        )
        await self.db.execute(query)

    async def soft_delete_descendants(self, pyramid_id: UUID, path_prefix: str):
        query = (
            update(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .where(PyramidNode.path.like(f"{path_prefix}%"))
            .values(is_deleted=True)
        )
        await self.db.execute(query)
