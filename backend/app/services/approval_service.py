import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate, ApprovalUpdate

class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_approval(self, schema: ApprovalCreate) -> Approval:
        db_obj = Approval(**schema.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_approval(self, id: uuid.UUID) -> Optional[Approval]:
        result = await self.db.execute(select(Approval).where(Approval.id == id))
        return result.scalar_one_or_none()

    async def get_pending_approvals(self, skip: int = 0, limit: int = 100) -> List[Approval]:
        query = select(Approval).where(Approval.status == "pending").offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def review_approval(self, id: uuid.UUID, schema: ApprovalUpdate) -> Optional[Approval]:
        approval = await self.get_approval(id)
        if not approval:
            return None
        
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(approval, key, value)
            
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
