import pytest
import uuid
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_batch_review_api_flow(client: AsyncClient, db_session):
    # 1. Create two approvals
    # We can use the service directly or API if available.
    # Let's use service to setup data to avoid API overhead or dependency.
    from app.services.approval_service import ApprovalService
    from app.schemas.approval import ApprovalCreate
    
    service = ApprovalService(db_session)
    
    schema1 = ApprovalCreate(type="create_node", source_content_id=uuid.uuid4(), data={"title": "Node 1"})
    approval1 = await service.create_approval(schema1)
    
    schema2 = ApprovalCreate(type="create_node", source_content_id=uuid.uuid4(), data={"title": "Node 2"})
    approval2 = await service.create_approval(schema2)
    
    # 2. Call batch review API (Approve)
    response = await client.post("/api/v1/approvals/batch/review", json={
        "ids": [str(approval1.id), str(approval2.id)],
        "action": "approve",
        "reason": "Batch API Test"
    })
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["success_count"] == 2
    assert data["failure_count"] == 0
    
    # Verify status
    updated1 = await service.get_approval(approval1.id)
    assert updated1.status == "approved"

@pytest.mark.asyncio
async def test_cleanup_api_flow(client: AsyncClient, db_session):
    # 1. Create approvals
    from app.services.approval_service import ApprovalService
    from app.schemas.approval import ApprovalCreate
    
    service = ApprovalService(db_session)
    
    # Create 3 pending
    for i in range(3):
        schema = ApprovalCreate(type="create_node", source_content_id=uuid.uuid4(), data={"title": f"Node {i}"})
        await service.create_approval(schema)
        
    # 2. Call cleanup API
    response = await client.post("/api/v1/approvals/cleanup", json={"reason": "Cleanup API Test"})
    
    assert response.status_code == 200
    data = response.json()["data"]
    # There might be other pending approvals from other tests if DB is shared/not cleaned?
    # But usually pytest-asyncio with proper fixture cleans up or uses transaction rollback.
    # Assuming at least 3.
    # Since we create fresh DB for each session in conftest (create_all/drop_all), it should be clean.
    # But wait, db_session creates tables once per session fixture?
    # The fixture scope is function by default (if not specified).
    # Yes, pytest_asyncio.fixture default scope is function.
    # So db is fresh.
    assert data["count"] >= 3
    
    # Verify empty
    # get_approvals expects status arg
    approvals = await service.get_approvals(status="pending")
    assert len(approvals) == 0
