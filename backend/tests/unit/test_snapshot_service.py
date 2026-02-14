import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.snapshot_service import SnapshotService
from app.models.snapshot import Snapshot
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation

import logging

@pytest.mark.asyncio
async def test_create_snapshot(db_session):
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    # Setup
    pyramid_id = uuid.uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid", description="Desc")
    
    node1 = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, name="Node 1", level=1, path="1")
    node2 = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, name="Node 2", level=2, parent_id=node1.id, path="1.2")
    
    db_session.add(pyramid)
    db_session.add(node1)
    db_session.add(node2)
    await db_session.flush()
    
    relation = NodeRelation(source_node_id=node1.id, target_node_id=node2.id, relation_type="parent")
    db_session.add(relation)
    await db_session.commit()
    
    # Execute
    service = SnapshotService(db_session)
    snapshot = await service.create_snapshot(pyramid_id, reason="Test Snapshot")
    
    # Verify
    assert snapshot is not None
    assert snapshot.pyramid_id == pyramid_id
    assert snapshot.reason == "Test Snapshot"
    assert snapshot.data["pyramid"]["id"] == str(pyramid_id)
    assert len(snapshot.data["nodes"]) == 2
    assert len(snapshot.data["relations"]) == 1
    assert snapshot.data["nodes"][0]["name"] in ["Node 1", "Node 2"]

@pytest.mark.asyncio
async def test_restore_snapshot(db_session):
    # Setup
    pyramid_id = uuid.uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid", description="Desc")
    db_session.add(pyramid)
    
    # Original state: Node A
    node_a = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, name="Node A", level=1, path="A")
    db_session.add(node_a)
    await db_session.commit()
    
    # Create Snapshot of state A
    service = SnapshotService(db_session)
    snapshot = await service.create_snapshot(pyramid_id, reason="State A")
    
    # Modify state: Delete Node A, Add Node B
    await db_session.delete(node_a)
    node_b = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, name="Node B", level=1, path="B")
    db_session.add(node_b)
    await db_session.commit()
    
    # Restore Snapshot
    success = await service.restore_snapshot(snapshot.id)
    assert success is True
    
    # Verify restoration
    # Since we are using the same session, we need to ensure the session is clean or query directly
    # In integration tests, session behavior is tricky.
    # Let's check if Node B is gone and Node A is back
    
    stmt = select(PyramidNode).where(PyramidNode.pyramid_id == pyramid_id)
    result = await db_session.execute(stmt)
    nodes = result.scalars().all()
    
    assert len(nodes) == 1
    assert nodes[0].name == "Node A"
    assert nodes[0].id == node_a.id

@pytest.mark.asyncio
async def test_rollback_creates_backup(db_session):
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    # Setup
    pyramid_id = uuid.uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid", description="Desc")
    db_session.add(pyramid)
    
    # State A
    node_a = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, name="Node A", level=1, path="A")
    db_session.add(node_a)
    await db_session.commit()
    
    # Create Snapshot 1 (Target for rollback)
    service = SnapshotService(db_session)
    snapshot_1 = await service.create_snapshot(pyramid_id, reason="Snapshot 1")
    
    # Change to State B
    # Modify Node A name to "Node A Modified"
    node_a.name = "Node A Modified"
    db_session.add(node_a)
    await db_session.commit()
    
    # Verify State B is active
    stmt = select(PyramidNode).where(PyramidNode.id == node_a.id)
    result = await db_session.execute(stmt)
    current_node = result.scalar_one()
    assert current_node.name == "Node A Modified"
    
    # Rollback to Snapshot 1
    success = await service.rollback(snapshot_1.id)
    assert success is True
    
    # Verify restoration to State A
    stmt = select(PyramidNode).where(PyramidNode.id == node_a.id)
    result = await db_session.execute(stmt)
    current_node = result.scalar_one()
    assert current_node.name == "Node A"
    
    # Verify Backup Snapshot was created
    stmt = select(Snapshot).where(Snapshot.pyramid_id == pyramid_id)
    result = await db_session.execute(stmt)
    snapshots = result.scalars().all()
    
    assert len(snapshots) == 2
    reasons = [s.reason for s in snapshots]
    assert "Snapshot 1" in reasons
    assert any(r.startswith("Auto-backup before rollback") for r in reasons if r)
    
    # The backup should contain State B ("Node A Modified")
    backup_snapshot = next(s for s in snapshots if s.reason and s.reason.startswith("Auto-backup"))
    assert backup_snapshot.data["nodes"][0]["name"] == "Node A Modified"
