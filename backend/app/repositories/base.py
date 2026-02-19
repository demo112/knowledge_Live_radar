from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self) -> int:
        query = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, obj_in: dict[str, Any], commit: bool = True) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        if commit:
            await self.db.commit()
            await self.db.refresh(db_obj)
        else:
            await self.db.flush()
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict[str, Any], commit: bool = True) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        if commit:
            await self.db.commit()
            await self.db.refresh(db_obj)
        else:
            await self.db.flush()
        return db_obj

    async def delete(self, id: UUID, commit: bool = True) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            if commit:
                await self.db.commit()
            else:
                await self.db.flush()
        return obj

    async def soft_delete(self, id: UUID, commit: bool = True) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj and hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            self.db.add(obj)
            if commit:
                await self.db.commit()
                await self.db.refresh(obj)
            else:
                await self.db.flush()
        return obj
