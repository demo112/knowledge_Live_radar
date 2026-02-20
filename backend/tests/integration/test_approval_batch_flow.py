import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.approval import Approval
from app.models.pyramid import Pyramid
import uuid

@pytest.mark.asyncio
async def test_batch_approval_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup Pyramid
    pyramid = Pyramid(name="Batch Test Pyramid", description="Testing Batch")
    db_session.add(pyramid)
    await db_session.commit()
    await db_session.refresh(pyramid)
    
    # 2. Create 3 approvals
    approvals = []
    ids = []
    for i in range(3):
        approval_id = uuid.uuid4()
        approval = Approval(
            id=approval_id,
            # pyramid_id removed as it is not a column
            type="ADD_NODE",
            status="pending",
            data={"name": f"Node {i}", "parent_id": None, "pyramid_id": str(pyramid.id)},
            confidence_score=0.8
        )
        db_session.add(approval)
        approvals.append(approval)
        ids.append(str(approval_id))
    await db_session.commit()
    
    # Verify created
    response = await client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    data = response.json()["data"]
    # Ensure our ids are in the response
    pending_ids = [item["id"] for item in data]
    for i in ids:
        assert i in pending_ids
    
    # 3. Batch Approve first 2
    approve_ids = ids[:2]
    response = await client.post(
        "/api/v1/approvals/batch/review",
        json={"ids": approve_ids, "action": "approve", "reason": "Batch OK"}
    )
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["success_count"] == 2
    
    # Verify status changed
    # They should be approved, not pending
    response = await client.get("/api/v1/approvals/pending")
    pending_ids = [item["id"] for item in response.json()["data"]]
    assert approve_ids[0] not in pending_ids
    assert approve_ids[1] not in pending_ids
    
    # 4. Batch Reject the 3rd one
    reject_ids = [ids[2]]
    response = await client.post(
        "/api/v1/approvals/batch/review",
        json={"ids": reject_ids, "action": "reject", "reason": "Batch NO"}
    )
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["success_count"] == 1
    
    # Verify DELETED (Physical deletion)
    # Check DB directly
    # Need to use a new session or expire? db_session is same.
    # AsyncSession.get needs to be awaited
    a3 = await db_session.get(Approval, uuid.UUID(reject_ids[0]))
    assert a3 is None 

@pytest.mark.asyncio
async def test_cleanup_flow(client: AsyncClient, db_session: AsyncSession):
    # Create 2 approvals
    pyramid = Pyramid(name="Cleanup Test Pyramid", description="Testing Cleanup")
    db_session.add(pyramid)
    await db_session.commit()
    await db_session.refresh(pyramid)
    
    approvals = []
    for i in range(2):
        approval = Approval(
            id=uuid.uuid4(),
            # pyramid_id removed
            type="ADD_NODE",
            status="pending",
            data={"name": f"Node {i}", "parent_id": None, "pyramid_id": str(pyramid.id)},
            confidence_score=0.8
        )
        db_session.add(approval)
        approvals.append(approval)
    await db_session.commit()
    
    # Verify created
    response = await client.get("/api/v1/approvals/pending")
    assert len(response.json()["data"]) >= 2
    
    # Cleanup
    response = await client.post(
        "/api/v1/approvals/cleanup",
        json={"reason": "Cleanup Test"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["count"] >= 2
    
    # Verify all gone
    response = await client.get("/api/v1/approvals/pending")
    assert len(response.json()["data"]) == 0
