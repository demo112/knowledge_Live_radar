import pytest
import uuid
from sqlalchemy import select
from app.services.snapshot_service import SnapshotService
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation

@pytest.mark.asyncio
async def test_snapshot_round_trip(db_session):
    # 1. Setup Pyramid
    pyramid = Pyramid(name="Snapshot Test", description="Testing rollback")
    db_session.add(pyramid)
    await db_session.commit()
    await db_session.refresh(pyramid)
    
    # 2. Setup Nodes
    root = PyramidNode(pyramid_id=pyramid.id, name="Root", level=0, path="root")
    db_session.add(root)
    await db_session.commit()
    await db_session.refresh(root)
    
    child1 = PyramidNode(pyramid_id=pyramid.id, name="Child 1", level=1, parent_id=root.id, path="root/c1")
    child2 = PyramidNode(pyramid_id=pyramid.id, name="Child 2", level=1, parent_id=root.id, path="root/c2")
    db_session.add_all([child1, child2])
    await db_session.commit()
    await db_session.refresh(child1)
    await db_session.refresh(child2)
    
    # 3. Setup Relations
    # Relation between siblings
    rel = NodeRelation(source_node_id=child1.id, target_node_id=child2.id, relation_type="sibling")
    db_session.add(rel)
    await db_session.commit()
    
    # 4. Create Snapshot
    service = SnapshotService(db_session)
    snapshot = await service.create_snapshot(pyramid.id, reason="Initial state")
    
    assert snapshot is not None
    assert snapshot.data["pyramid"]["name"] == "Snapshot Test"
    assert len(snapshot.data["nodes"]) == 3
    assert len(snapshot.data["relations"]) == 1
    
    # 5. Modify State (Simulate Drift or Error)
    # Delete child2 (and relation should cascade delete)
    await db_session.delete(child2)
    
    # Add a new node that shouldn't be there after restore
    new_node = PyramidNode(pyramid_id=pyramid.id, name="New Node", level=1, parent_id=root.id, path="root/new")
    db_session.add(new_node)
    
    await db_session.commit()
    
    # Verify modification
    stmt = select(PyramidNode).where(PyramidNode.pyramid_id == pyramid.id)
    result = await db_session.execute(stmt)
    current_nodes = result.scalars().all()
    names = [n.name for n in current_nodes]
    assert "Child 2" not in names
    assert "New Node" in names
    assert len(current_nodes) == 3 # Root, Child 1, New Node
    
    # Verify relation gone
    stmt_rel = select(NodeRelation).where(NodeRelation.source_node_id == child1.id)
    result_rel = await db_session.execute(stmt_rel)
    assert len(result_rel.scalars().all()) == 0
    
    # 6. Restore Snapshot
    success = await service.restore_snapshot(snapshot.id)
    assert success is True
    
    # 7. Verify Restoration
    # Check nodes
    result = await db_session.execute(stmt)
    restored_nodes = result.scalars().all()
    restored_names = [n.name for n in restored_nodes]
    
    assert len(restored_nodes) == 3
    assert "Root" in restored_names
    assert "Child 1" in restored_names
    assert "Child 2" in restored_names
    assert "New Node" not in restored_names
    
    # Check relations
    result_rel = await db_session.execute(stmt_rel)
    restored_rels = result_rel.scalars().all()
    assert len(restored_rels) == 1
    assert restored_rels[0].target_node_id == child2.id
