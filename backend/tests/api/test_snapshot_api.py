import pytest
import uuid
from datetime import datetime, timezone
from app.models.snapshot import Snapshot
from app.models.pyramid import Pyramid

async def test_create_snapshot_api(client, db_session):
    # Create a pyramid
    pyramid = Pyramid(
        id=uuid.uuid4(),
        name="Test Pyramid",
        description="For snapshot test"
    )
    db_session.add(pyramid)
    await db_session.commit()

    # Create snapshot
    response = await client.post(
        f"/api/v1/pyramids/{pyramid.id}/snapshots",
        json={"reason": "Test Snapshot"}
    )
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["pyramid_id"] == str(pyramid.id)
    assert data["reason"] == "Test Snapshot"
    assert "version" in data

async def test_get_snapshots_api(client, db_session):
    # Create a pyramid
    pyramid = Pyramid(
        id=uuid.uuid4(),
        name="Test Pyramid 2",
        description="For snapshot list test"
    )
    db_session.add(pyramid)
    await db_session.commit()

    # Create manual snapshot
    snapshot = Snapshot(
        id=uuid.uuid4(),
        pyramid_id=pyramid.id,
        version="v-1",
        reason="Manual",
        data={"nodes": [], "pyramid": {}, "timestamp": datetime.now(timezone.utc).isoformat()}
    )
    db_session.add(snapshot)
    await db_session.commit()

    # Get snapshots
    response = await client.get(f"/api/v1/pyramids/{pyramid.id}/snapshots")
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) >= 1
    assert data["items"][0]["id"] == str(snapshot.id)

async def test_get_snapshot_details_api(client, db_session):
    # Create a pyramid
    pyramid = Pyramid(
        id=uuid.uuid4(),
        name="Test Pyramid 3",
        description="For snapshot detail test"
    )
    db_session.add(pyramid)
    await db_session.commit()

    # Create manual snapshot
    snapshot = Snapshot(
        id=uuid.uuid4(),
        pyramid_id=pyramid.id,
        version="v-detail",
        reason="Detail",
        data={"nodes": [], "pyramid": {}, "timestamp": datetime.now(timezone.utc).isoformat()}
    )
    db_session.add(snapshot)
    await db_session.commit()

    # Get snapshot detail
    response = await client.get(f"/api/v1/pyramids/{pyramid.id}/snapshots/{snapshot.id}")
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(snapshot.id)
    assert data["data"] is not None

async def test_rollback_api(client, db_session):
    # Create a pyramid
    pyramid = Pyramid(
        id=uuid.uuid4(),
        name="Test Pyramid Rollback",
        description="For rollback test"
    )
    db_session.add(pyramid)
    await db_session.commit()

    # Create manual snapshot
    snapshot = Snapshot(
        id=uuid.uuid4(),
        pyramid_id=pyramid.id,
        version="v-rollback",
        reason="Rollback",
        data={
            "nodes": [], 
            "relations": [],
            "pyramid": {"id": str(pyramid.id), "name": pyramid.name, "description": pyramid.description}, 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    db_session.add(snapshot)
    await db_session.commit()

    # Rollback
    response = await client.post(f"/api/v1/pyramids/{pyramid.id}/rollback/{snapshot.id}")
    
    assert response.status_code == 200
    assert response.json()["data"] is True
