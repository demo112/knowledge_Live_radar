import logging
import uuid
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.snapshot import Snapshot
from app.models.pyramid import Pyramid, PyramidNode

logger = logging.getLogger(__name__)

class SnapshotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_snapshot(self, pyramid_id: uuid.UUID, reason: str = "Manual snapshot") -> Snapshot:
        """
        Create a snapshot of the current pyramid state.
        """
        logger.info(f"Creating snapshot for pyramid {pyramid_id}")
        
        # 1. Fetch Pyramid Data
        stmt = select(Pyramid).where(Pyramid.id == pyramid_id)
        result = await self.db.execute(stmt)
        pyramid = result.scalar_one_or_none()
        
        if not pyramid:
            raise ValueError(f"Pyramid {pyramid_id} not found")

        # 2. Fetch Nodes (recursively or flat list)
        # Using flat list for simplicity in snapshot
        stmt_nodes = select(PyramidNode).where(PyramidNode.pyramid_id == pyramid_id)
        result_nodes = await self.db.execute(stmt_nodes)
        nodes = result_nodes.scalars().all()
        
        # 3. Serialize Data
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
            
        snapshot_data = {
            "pyramid": {
                "id": str(pyramid.id),
                "name": pyramid.name,
                "description": pyramid.description
            },
            "nodes": nodes_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 4. Create Snapshot Record
        version = f"v-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
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

    async def restore_snapshot(self, snapshot_id: uuid.UUID):
        """
        Restore a pyramid to a previous state.
        WARNING: This is a destructive operation.
        """
        # For Iteration 3, we might not need full restore functionality yet, 
        # but it's good to have the structure.
        # Implementation would involve:
        # 1. Load snapshot data
        # 2. Delete current nodes
        # 3. Recreate nodes from snapshot data
        logger.warning("Restore snapshot not fully implemented yet")
        pass

    async def get_snapshots_by_pyramid(self, pyramid_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Snapshot]:
        stmt = select(Snapshot).where(Snapshot.pyramid_id == pyramid_id).order_by(Snapshot.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
