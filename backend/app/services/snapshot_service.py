import logging
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.snapshot import Snapshot
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation

logger = logging.getLogger(__name__)

class SnapshotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_snapshot(self, pyramid_id: uuid.UUID, reason: str = "Manual snapshot") -> Snapshot:
        """
        Create a snapshot of the current pyramid state (nodes + relations).
        """
        logger.info(f"Creating snapshot for pyramid {pyramid_id}")
        
        # 1. Fetch Pyramid Data
        stmt = select(Pyramid).where(Pyramid.id == pyramid_id)
        result = await self.db.execute(stmt)
        pyramid = result.scalar_one_or_none()
        
        if not pyramid:
            raise ValueError(f"Pyramid {pyramid_id} not found")

        # 2. Fetch Nodes
        stmt_nodes = select(PyramidNode).where(PyramidNode.pyramid_id == pyramid_id)
        result_nodes = await self.db.execute(stmt_nodes)
        nodes = result_nodes.scalars().all()
        node_ids = [node.id for node in nodes]
        
        # 3. Fetch Relations
        relations = []
        if node_ids:
            stmt_relations = select(NodeRelation).where(
                (NodeRelation.source_node_id.in_(node_ids)) | 
                (NodeRelation.target_node_id.in_(node_ids))
            )
            result_relations = await self.db.execute(stmt_relations)
            relations = result_relations.scalars().all()
        
        # 4. Serialize Data
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                "id": str(node.id),
                "parent_id": str(node.parent_id) if node.parent_id else None,
                "name": node.name,
                "description": node.description,
                "level": node.level,
                "sort_order": node.sort_order,
                "path": node.path,
                "health_score": node.health_score
            })
            
        relations_data = []
        for rel in relations:
            relations_data.append({
                "id": str(rel.id),
                "source_node_id": str(rel.source_node_id),
                "target_node_id": str(rel.target_node_id),
                "relation_type": rel.relation_type
            })
            
        snapshot_data = {
            "pyramid": {
                "id": str(pyramid.id),
                "name": pyramid.name,
                "description": pyramid.description
            },
            "nodes": nodes_data,
            "relations": relations_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 5. Create Snapshot Record
        version = f"v-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        snapshot = Snapshot(
            pyramid_id=pyramid_id,
            version=version,
            data=snapshot_data,
            reason=reason
        )
        
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        
        logger.info(f"Snapshot {snapshot.id} created with version {version}")
        return snapshot

    def _validate_snapshot_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the snapshot data has the required structure.
        """
        if not isinstance(data, dict):
            return False
            
        required_keys = ["pyramid", "nodes", "timestamp"]
        if not all(key in data for key in required_keys):
            return False
            
        if not isinstance(data["nodes"], list):
            return False
            
        if "relations" in data and not isinstance(data["relations"], list):
            return False
            
        return True

    async def rollback(self, snapshot_id: uuid.UUID) -> bool:
        """
        Rollback to a specific snapshot, creating a backup of the current state first.
        """
        # 1. Fetch snapshot to get pyramid_id
        snapshot = await self.get_snapshot_by_id(snapshot_id)
        if not snapshot:
            logger.error(f"Snapshot {snapshot_id} not found")
            return False
        
        # 2. Create backup of current state
        try:
            await self.create_snapshot(
                pyramid_id=snapshot.pyramid_id, 
                reason=f"Auto-backup before rollback to {snapshot.version}"
            )
        except Exception as e:
            logger.error(f"Failed to create backup snapshot: {e}")
            return False # Abort rollback if backup fails
        
        # 3. Perform restore
        return await self.restore_snapshot(snapshot_id)

    async def restore_snapshot(self, snapshot_id: uuid.UUID) -> bool:
        """
        Restore a pyramid to a previous state.
        WARNING: This is a destructive operation for current data.
        """
        logger.info(f"Restoring snapshot {snapshot_id}")
        
        # 1. Fetch Snapshot
        stmt = select(Snapshot).where(Snapshot.id == snapshot_id)
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            logger.error(f"Snapshot {snapshot_id} not found")
            return False
            
        data = snapshot.data
        if not self._validate_snapshot_data(data):
            logger.error(f"Invalid snapshot data for {snapshot_id}")
            return False
            
        pyramid_id = snapshot.pyramid_id
        
        # 2. Verify Pyramid Exists
        stmt_pyramid = select(Pyramid).where(Pyramid.id == pyramid_id)
        result_pyramid = await self.db.execute(stmt_pyramid)
        current_pyramid = result_pyramid.scalar_one_or_none()
        
        if not current_pyramid:
            logger.error(f"Pyramid {pyramid_id} not found for restore")
            return False

        try:
            # 3. Clear Current State
            # Note: NodeRelation has ON DELETE CASCADE on source_node_id/target_node_id
            # So deleting nodes should clear relations too.
            # But to be safe and explicit, or if CASCADE is not reliable in SQLite without pragma:
            
            # Fetch current node IDs to be safe? 
            # Or just delete nodes by pyramid_id
            await self.db.execute(
                delete(PyramidNode).where(PyramidNode.pyramid_id == pyramid_id)
            )
            
            # 4. Recreate Nodes from Snapshot
            nodes_data = data.get("nodes", [])
            # Sort by level to ensure parents exist before children
            nodes_data.sort(key=lambda x: x.get("level", 0))
            
            # We must map IDs to UUID objects
            # And we MUST reuse the IDs from snapshot to preserve internal consistency (parent_id)
            
            for node_data in nodes_data:
                node = PyramidNode(
                    id=uuid.UUID(node_data["id"]),
                    pyramid_id=pyramid_id,
                    parent_id=uuid.UUID(node_data["parent_id"]) if node_data.get("parent_id") else None,
                    name=node_data["name"],
                    description=node_data.get("description"),
                    level=node_data.get("level", 0),
                    sort_order=node_data.get("sort_order", 0),
                    path=node_data.get("path", ""),
                    health_score=node_data.get("health_score")
                )
                self.db.add(node)
            
            # Flush to ensure nodes exist before adding relations
            await self.db.flush()
            
            # 5. Recreate Relations
            relations_data = data.get("relations", [])
            for rel_data in relations_data:
                # Check if nodes exist in the snapshot (they should)
                # But if snapshot captured relations to nodes OUTSIDE the pyramid (if possible),
                # those might fail if we don't restore them.
                # Assuming all relations are internal or valid.
                
                # Check if relation already exists (it shouldn't since we cleared everything)
                
                rel = NodeRelation(
                    id=uuid.UUID(rel_data["id"]) if "id" in rel_data else uuid.uuid4(),
                    source_node_id=uuid.UUID(rel_data["source_node_id"]),
                    target_node_id=uuid.UUID(rel_data["target_node_id"]),
                    relation_type=rel_data.get("relation_type", "related")
                )
                self.db.add(rel)
                
            # 6. Restore Pyramid Metadata if changed?
            # Keeping it simple for now.
            
            await self.db.commit()
            logger.info(f"Successfully restored snapshot {snapshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore snapshot {snapshot_id}: {e}")
            await self.db.rollback()
            return False

    async def get_snapshots_by_pyramid(self, pyramid_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Snapshot]:
        stmt = select(Snapshot).where(Snapshot.pyramid_id == pyramid_id).order_by(Snapshot.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_snapshot_by_id(self, snapshot_id: uuid.UUID) -> Optional[Snapshot]:
        stmt = select(Snapshot).where(Snapshot.id == snapshot_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
