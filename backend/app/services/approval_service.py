import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate, ApprovalUpdate, BatchReviewRequest, BatchReviewResult, CleanupRequest, CleanupResult

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

    async def get_approvals(self, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Approval]:
        query = select(Approval)
        if status:
            query = query.where(Approval.status == status)
        
        query = query.order_by(Approval.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def review_approval(self, id: uuid.UUID, schema: ApprovalUpdate) -> Optional[Approval]:
        approval = await self.get_approval(id)
        if not approval:
            return None
        
        old_status = approval.status
        
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(approval, key, value)
            
        await self.db.commit()
        await self.db.refresh(approval)
        
        # if old_status != approval.status:
        #     from app.services.notification_service import notification_service
        #     await notification_service.notify_approval_status_change(approval, old_status, approval.status)
        
        return approval

    async def execute_approval(self, id: uuid.UUID, user_id: str = "system") -> bool:
        """
        Execute an approved proposal.
        """
        from app.services.decision_executor import DecisionExecutor
        executor = DecisionExecutor(self.db)
        return await executor.execute_approval(id, user_id)

    async def rollback_execution(self, id: uuid.UUID) -> bool:
        """
        Rollback an executed proposal.
        """
        from app.services.decision_executor import DecisionExecutor
        executor = DecisionExecutor(self.db)
        return await executor.rollback_execution(id)

    async def batch_review(self, request: BatchReviewRequest) -> BatchReviewResult:
        success_count = 0
        failure_count = 0
        failures = []

        for id in request.ids:
            approval = await self.get_approval(id)
            if not approval:
                failure_count += 1
                failures.append({"id": str(id), "error": "Approval not found"})
                continue
            
            try:
                if request.action == "approve":
                    approval.status = "approved"
                    # Apply reason if provided? The request has reason, but Approval model might not store it directly
                    # unless we want to store it in data or review_comment. 
                    # The ApprovalUpdate schema has review_comment.
                    if request.reason:
                        approval.review_comment = request.reason
                elif request.action == "reject":
                    await self.db.delete(approval)
                
                success_count += 1
            except Exception as e:
                failure_count += 1
                failures.append({"id": str(id), "error": str(e)})

        await self.db.commit()
        return BatchReviewResult(
            success_count=success_count,
            failure_count=failure_count,
            failures=failures
        )

    async def cleanup_pending_approvals(self, request: CleanupRequest) -> CleanupResult:
        query = select(Approval).where(Approval.status == "pending")
        result = await self.db.execute(query)
        approvals = result.scalars().all()
        
        count = len(approvals)
        for approval in approvals:
            await self.db.delete(approval)
            
        await self.db.commit()
        
        return CleanupResult(
            count=count,
            message=f"Successfully cleaned up {count} pending approvals."
        )


