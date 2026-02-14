import pytest
import uuid
from app.models.pyramid import Pyramid, PyramidNode
from app.models.snapshot import Snapshot
from app.services.snapshot_service import SnapshotService
from app.services.pyramid_service import PyramidService
from sqlalchemy import select

async def test_snapshot_lifecycle_verification(db_session):
    """
    Task 21: Verify Snapshot Functionality (Full Lifecycle)
    1. Create Pyramid & Nodes
    2. Create Snapshot V1
    3. Modify Nodes
    4. Create Snapshot V2
    5. Rollback to V1
    6. Verify State
    """
    snapshot_service = SnapshotService(db_session)
    pyramid_service = PyramidService(db_session)
    
    # 1. Create Pyramid
    pyramid = Pyramid(
        id=uuid.uuid4(),
        name="Lifecycle Pyramid",
        description="Testing snapshot lifecycle"
    )
    db_session.add(pyramid)
    await db_session.commit()
    
    pyramid_id = pyramid.id
    
    # Add initial nodes
    node1 = PyramidNode(
        id=uuid.uuid4(),
        pyramid_id=pyramid_id,
        name="Node 1",
        description="Initial content",
        path="001"
    )
    db_session.add(node1)
    await db_session.commit()
    
    # 2. Create Snapshot V1
    v1_snapshot = await snapshot_service.create_snapshot(pyramid_id, "V1 Initial")
    assert v1_snapshot is not None
    
    # 3. Modify Nodes (Update Node 1, Add Node 2)
    node1.description = "Modified content"
    db_session.add(node1)
    
    node2 = PyramidNode(
        id=uuid.uuid4(),
        pyramid_id=pyramid_id,
        name="Node 2",
        description="New node",
        path="002"
    )
    db_session.add(node2)
    await db_session.commit()
    
    # Verify modification
    current_nodes = await pyramid_service.get_nodes(pyramid_id)
    assert len(current_nodes) == 2
    
    # Sort nodes to ensure consistent order for checking
    sorted_nodes = sorted(current_nodes, key=lambda x: x.path)
    # Check if any node has the modified content
    assert any(n.description == "Modified content" for n in current_nodes)
    
    # 4. Create Snapshot V2
    v2_snapshot = await snapshot_service.create_snapshot(pyramid_id, "V2 Modified")
    assert v2_snapshot is not None
    
    # 5. Rollback to V1
    success = await snapshot_service.restore_snapshot(v1_snapshot.id)
    assert success is True
    
    # 6. Verify State (Should be back to Node 1 with "Initial content", Node 2 gone)
    # Need to expire/refresh session or fetch fresh
    db_session.expire_all()
    
    restored_nodes = await pyramid_service.get_nodes(pyramid_id)
    assert len(restored_nodes) == 1
    assert restored_nodes[0].id == node1.id
    assert restored_nodes[0].description == "Initial content"
    assert restored_nodes[0].name == "Node 1"
    
    print("Snapshot Lifecycle Verification Passed!")
