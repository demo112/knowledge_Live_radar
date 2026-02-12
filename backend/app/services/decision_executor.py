import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.approval import Approval
from app.models.pyramid import PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.services.snapshot_service import SnapshotService

logger = logging.getLogger(__name__)

class DecisionExecutor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.snapshot_service = SnapshotService(db)

    async def execute_approval(self, approval_id: uuid.UUID, user_id: str) -> bool:
        """
        Execute an approved change proposal.
        """
        logger.info(f"Executing approval {approval_id} by user {user_id}")
        
        stmt = select(Approval).where(Approval.id == approval_id)
        result = await self.db.execute(stmt)
        approval = result.scalar_one_or_none()
        
        if not approval:
            logger.error(f"Approval {approval_id} not found")
            return False
            
        if approval.status != "approved":
            logger.error(f"Approval {approval_id} is not in approved status (current: {approval.status})")
            return False

        try:
            # 1. Create Snapshot (Safety first)
            # Assuming we can get pyramid_id from data or context. 
            # For create_node, pyramid_id is in data.
            # For link_content, we need to find the node to get pyramid_id.
            pyramid_id = None
            if "pyramid_id" in approval.data:
                pyramid_id = uuid.UUID(approval.data["pyramid_id"])
            elif "node_id" in approval.data:
                node_id = uuid.UUID(approval.data["node_id"])
                stmt_node = select(PyramidNode).where(PyramidNode.id == node_id)
                result_node = await self.db.execute(stmt_node)
                node = result_node.scalar_one_or_none()
                if node:
                    pyramid_id = node.pyramid_id
            
            if pyramid_id:
                await self.snapshot_service.create_snapshot(pyramid_id, reason=f"Pre-execution of approval {approval_id}")

            # 2. Execute Change based on Type
            if approval.type == "create_node":
                await self._execute_create_node(approval)
            elif approval.type == "link_content":
                await self._execute_link_content(approval)
            else:
                logger.warning(f"Unknown approval type: {approval.type}")
                return False

            # 3. Update Approval Status
            old_status = approval.status
            approval.status = "executed"
            # approval.executed_at = datetime.utcnow() # If we had this field
            
            await self.db.commit()
            logger.info(f"Approval {approval_id} executed successfully")
            
            from app.services.notification_service import notification_service
            await notification_service.notify_approval_status_change(approval, old_status, "executed")

            return True

        except Exception as e:
            logger.error(f"Failed to execute approval {approval_id}: {e}")
            await self.db.rollback()
            return False

    async def _execute_create_node(self, approval: Approval):
        data = approval.data
        new_node = PyramidNode(
            pyramid_id=uuid.UUID(data["pyramid_id"]),
            parent_id=uuid.UUID(data["parent_id"]) if data.get("parent_id") else None,
            name=data["name"],
            description=data.get("description"),
            level=0, # Should calculate level based on parent
            path="" # Should calculate path
        )
        # Logic to calculate level and path... simplified for now
        
        self.db.add(new_node)
        # We need to flush to get ID if we were to use it immediately, but commit happens in main method
    
    async def _execute_link_content(self, approval: Approval):
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        content_id = uuid.UUID(data["content_id"])
        
        # Check if relation already exists
        stmt = select(ContentNodeRelation).where(
            ContentNodeRelation.node_id == node_id,
            ContentNodeRelation.content_id == content_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            relation = ContentNodeRelation(
                node_id=node_id,
                content_id=content_id,
                confidence=approval.confidence_score or 1.0,
                is_manual=False # Or True if approved by human? Let's say False as it's AI generated originally
            )
            self.db.add(relation)
