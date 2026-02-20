import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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
            elif approval.type == "split_node":
                await self._execute_split_node(approval)
            elif approval.type == "merge_node":
                await self._execute_merge_node(approval)
            elif approval.type == "move_node":
                await self._execute_move_node(approval)
            elif approval.type == "fix_drift":
                await self._execute_fix_drift(approval)
            elif approval.type == "delete_node":
                await self._execute_delete_node(approval)
            elif approval.type == "update_strategy":
                await self._execute_update_strategy(approval)
            else:
                logger.warning(f"Unknown approval type: {approval.type}")
                return False

            # 3. Update Approval Status
            old_status = approval.status
            approval.status = "executed"
            approval.executed_at = func.now()
            
            await self.db.commit()
            logger.info(f"Approval {approval_id} executed successfully")
            
            from app.services.notification_service import notification_service
            await notification_service.notify_approval_status_change(approval, old_status, "executed")

            return True

        except Exception as e:
            logger.error(f"Failed to execute approval {approval_id}: {e}")
            await self.db.rollback()
            return False

    async def rollback_execution(self, approval_id: uuid.UUID) -> bool:
        """
        Rollback an executed approval by restoring the snapshot taken before it.
        """
        logger.info(f"Rolling back approval {approval_id}")
        
        stmt = select(Approval).where(Approval.id == approval_id)
        result = await self.db.execute(stmt)
        approval = result.scalar_one_or_none()
        
        if not approval:
            logger.error(f"Approval {approval_id} not found")
            return False
            
        if approval.status != "executed":
            logger.error(f"Approval {approval_id} is not executed (current: {approval.status})")
            return False

        # Find the snapshot taken for this approval
        # We look for snapshots created around the time of execution with the specific reason
        # Or better, we should have linked snapshot to approval, but we didn't.
        # We rely on the reason string: "Pre-execution of approval {approval_id}"
        
        from app.models.snapshot import Snapshot
        stmt_snap = select(Snapshot).where(
            Snapshot.reason == f"Pre-execution of approval {approval_id}"
        ).order_by(Snapshot.created_at.desc())
        
        result_snap = await self.db.execute(stmt_snap)
        snapshot = result_snap.scalar_one_or_none()
        
        if not snapshot:
            logger.error(f"No snapshot found for approval {approval_id}")
            return False
            
        # Restore
        success = await self.snapshot_service.restore_snapshot(snapshot.id)
        
        if success:
            approval.status = "rolled_back"
            await self.db.commit()
            logger.info(f"Approval {approval_id} rolled back successfully")
            return True
            
        return False

    async def _execute_create_node(self, approval: Approval):
        data = approval.data
        pyramid_id = uuid.UUID(data["pyramid_id"])
        parent_id = uuid.UUID(data["parent_id"]) if data.get("parent_id") else None

        # Calculate level and path based on parent
        level = 0
        path = ""
        if parent_id:
            parent_result = await self.db.execute(
                select(PyramidNode).where(PyramidNode.id == parent_id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                level = parent.level + 1
                parent_path = parent.path or str(parent.id)
                path = f"{parent_path}/{parent.id}"

        new_node = PyramidNode(
            pyramid_id=pyramid_id,
            parent_id=parent_id,
            name=data["name"],
            description=data.get("description"),
            level=level,
            path=path,
        )
        self.db.add(new_node)
        await self.db.flush()
        logger.info(f"Created node '{data['name']}' at level {level}")
    
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

    async def _execute_split_node(self, approval: Approval):
        """Split a node into sub-categories based on AI suggestion."""
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        
        stmt = select(PyramidNode).where(PyramidNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        if not node:
            raise ValueError(f"Node {node_id} not found for split")

        # Get suggested sub-categories from data, or create generic ones
        sub_names = data.get("suggested_children", [f"{node.name} - Part A", f"{node.name} - Part B"])
        
        for i, name in enumerate(sub_names):
            child = PyramidNode(
                pyramid_id=node.pyramid_id,
                parent_id=node.id,
                name=name,
                description=f"Auto-created from split of '{node.name}'",
                level=node.level + 1,
                sort_order=i,
            )
            self.db.add(child)
        
        logger.info(f"Split node '{node.name}' into {len(sub_names)} children")

    async def _execute_merge_node(self, approval: Approval):
        """Merge a sparse node's children into its parent or sibling."""
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        
        stmt = select(PyramidNode).where(PyramidNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        if not node:
            raise ValueError(f"Node {node_id} not found for merge")

        # Move all children up to this node's parent
        children_result = await self.db.execute(
            select(PyramidNode).where(
                PyramidNode.parent_id == node_id,
                PyramidNode.is_deleted == False,
            )
        )
        children = children_result.scalars().all()
        
        for child in children:
            child.parent_id = node.parent_id
            child.level = max(0, child.level - 1)

        # Move content relations from this node to parent
        if node.parent_id:
            relations_result = await self.db.execute(
                select(ContentNodeRelation).where(ContentNodeRelation.node_id == node_id)
            )
            for rel in relations_result.scalars().all():
                rel.node_id = node.parent_id

        # Soft-delete the merged node
        node.is_deleted = True
        logger.info(f"Merged node '{node.name}' into parent, moved {len(children)} children")

    async def _execute_move_node(self, approval: Approval):
        """Move a node to a different parent (flatten deep hierarchy)."""
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        
        stmt = select(PyramidNode).where(PyramidNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        if not node:
            raise ValueError(f"Node {node_id} not found for move")

        # Move up by reducing level — find grandparent
        if node.parent_id:
            parent_result = await self.db.execute(
                select(PyramidNode).where(PyramidNode.id == node.parent_id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent and parent.parent_id:
                node.parent_id = parent.parent_id
                node.level = max(0, node.level - 1)
                logger.info(f"Moved node '{node.name}' up one level (flatten)")
            else:
                logger.warning(f"Cannot move node '{node.name}' further up — already near root")

    async def _execute_fix_drift(self, approval: Approval):
        """Update node description based on detected concept drift."""
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        
        stmt = select(PyramidNode).where(PyramidNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        if not node:
            raise ValueError(f"Node {node_id} not found for drift fix")

        new_description = data.get("new_description") or data.get("drift_analysis", "")
        if new_description:
            old_desc = node.description
            node.description = f"{node.description or ''}\n[Updated due to concept drift: {new_description}]".strip()
            logger.info(f"Updated node '{node.name}' description due to concept drift")

    async def _execute_delete_node(self, approval: Approval):
        """Soft-delete a node and reassign its content."""
        data = approval.data
        node_id = uuid.UUID(data["node_id"])
        
        stmt = select(PyramidNode).where(PyramidNode.id == node_id)
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        if not node:
            raise ValueError(f"Node {node_id} not found for deletion")

        # Move children to parent
        children_result = await self.db.execute(
            select(PyramidNode).where(
                PyramidNode.parent_id == node_id,
                PyramidNode.is_deleted == False,
            )
        )
        for child in children_result.scalars().all():
            child.parent_id = node.parent_id
            child.level = max(0, child.level - 1)

        # Move content to parent node if exists
        if node.parent_id:
            relations_result = await self.db.execute(
                select(ContentNodeRelation).where(ContentNodeRelation.node_id == node_id)
            )
            for rel in relations_result.scalars().all():
                rel.node_id = node.parent_id

        node.is_deleted = True
        logger.info(f"Soft-deleted node '{node.name}'")

    async def _execute_update_strategy(self, approval: Approval):
        """Update crawl strategy for a source."""
        from app.models.source import InformationSource
        
        data = approval.data
        source_id = data.get("source_id")
        if not source_id:
            raise ValueError("source_id missing in strategy update approval")

        stmt = select(InformationSource).where(InformationSource.id == uuid.UUID(source_id))
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()
        if not source:
            raise ValueError(f"Source {source_id} not found for strategy update")

        # Apply strategy changes from data
        if "new_interval" in data:
            old_interval = source.check_interval
            source.check_interval = int(data["new_interval"])
            logger.info(f"Updated source '{source.name}' interval: {old_interval} -> {source.check_interval}")

        if "new_timeout" in data:
            # If source model has timeout field
            if hasattr(source, 'timeout'):
                source.timeout = int(data["new_timeout"])
                logger.info(f"Updated source '{source.name}' timeout to {source.timeout}")
