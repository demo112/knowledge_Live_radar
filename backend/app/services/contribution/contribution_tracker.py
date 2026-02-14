from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.contribution import Contribution
import uuid
from datetime import datetime, timedelta

class ContributionTracker:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contribution(self, 
                                user_id: Optional[str], 
                                input_type: str, 
                                original_input: str,
                                content_id: Optional[uuid.UUID] = None) -> Contribution:
        """Create a new contribution record."""
        contribution = Contribution(
            user_id=user_id,
            input_type=input_type,
            original_input=original_input,
            content_id=content_id,
            status="pending"
        )
        self.db.add(contribution)
        await self.db.commit()
        await self.db.refresh(contribution)
        return contribution

    async def update_status(self, 
                          contribution_id: uuid.UUID, 
                          status: str, 
                          extracted_content: Optional[str] = None,
                          extracted_concepts: Optional[List[dict]] = None,
                          rejection_reason: Optional[str] = None) -> Optional[Contribution]:
        """Update contribution status and results."""
        stmt = select(Contribution).where(Contribution.id == contribution_id)
        result = await self.db.execute(stmt)
        contribution = result.scalars().first()
        
        if not contribution:
            return None
            
        contribution.status = status
        if extracted_content is not None:
            contribution.extracted_content = extracted_content
        if extracted_concepts is not None:
            contribution.extracted_concepts = extracted_concepts
        if rejection_reason is not None:
            contribution.rejection_reason = rejection_reason
            
        await self.db.commit()
        await self.db.refresh(contribution)
        return contribution

    async def get_user_contributions(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Contribution]:
        """Get contributions for a specific user."""
        stmt = select(Contribution).where(
            Contribution.user_id == user_id
        ).order_by(desc(Contribution.created_at)).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_contributions(self, limit: int = 50) -> List[Contribution]:
        """Get recent contributions from all users."""
        stmt = select(Contribution).order_by(desc(Contribution.created_at)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_contribution(self, contribution_id: uuid.UUID) -> Optional[Contribution]:
        """Get a specific contribution by ID."""
        stmt = select(Contribution).where(Contribution.id == contribution_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_stats(self, days: int = 30) -> Dict:
        """Get contribution statistics for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total count
        total_stmt = select(func.count(Contribution.id)).where(Contribution.created_at >= start_date)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # Count by status
        status_stmt = select(Contribution.status, func.count(Contribution.id)).where(
            Contribution.created_at >= start_date
        ).group_by(Contribution.status)
        status_result = await self.db.execute(status_stmt)
        by_status = {row[0]: row[1] for row in status_result.all()}
        
        # Count by type
        type_stmt = select(Contribution.input_type, func.count(Contribution.id)).where(
            Contribution.created_at >= start_date
        ).group_by(Contribution.input_type)
        type_result = await self.db.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type,
            "period_days": days
        }
