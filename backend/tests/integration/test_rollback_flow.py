
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pyramid import PyramidNode

from app.models.approval import Approval

@pytest.mark.asyncio
async def test_rollback_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup: Create Pyramid
    response = await client.post(
        "/api/v1/pyramids",
        json={"name": "Rollback Pyramid", "description": "For Rollback Test"}
    )
    assert response.status_code == 201
    pyramid_id = response.json()["data"]["id"]

    # 2. Submit & Analyze to get Approval
    response = await client.post(
        "/api/v1/contents/text", 
        json={"text": "Rollback content", "title": "RB", "submitter_id": "tester"}
    )
    content_id = response.json()["data"]["id"]

    # Pre-create the approval
    approval_id_uuid = uuid.uuid4()
    approval = Approval(
        id=approval_id_uuid,
        type="create_node",
        status="pending",
        data={"name": "RollbackNode", "pyramid_id": pyramid_id},
        source_content_id=uuid.UUID(content_id),
        confidence_score=0.95,
        generated_by="ai"
    )
    db_session.add(approval)
    await db_session.commit()

    with patch("app.services.content_analyzer.ContentAnalyzer.analyze_content") as mock_analyze:
        mock_analyze.return_value = [{
            "id": str(approval_id_uuid),
            "type": "create_node",
            "status": "pending",
            "data": {"name": "RollbackNode", "pyramid_id": pyramid_id},
            "source_content_id": content_id,
            "pyramid_id": pyramid_id,
            "confidence_score": 0.95,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "reviewer_id": None,
            "review_comment": None,
            "review_comments": []
        }]
        
        await client.post(
            f"/api/v1/contents/{content_id}/analyze",
            json={"pyramid_id": pyramid_id}
        )

    # 3. Approve and Execute
    approvals = (await client.get("/api/v1/approvals/pending")).json()["data"]
    approval_id = approvals[0]["id"]
    
    await client.post(
        f"/api/v1/approvals/{approval_id}/review",
        json={"status": "approved", "reviewer_id": "admin"}
    )
    
    await client.post(f"/api/v1/approvals/{approval_id}/execute")
    
    # Verify Node Exists
    # We can check DB directly via db_session for more reliability in integration test
    stmt = select(PyramidNode).where(PyramidNode.pyramid_id == uuid.UUID(pyramid_id))
    result = await db_session.execute(stmt)
    nodes = result.scalars().all()
    assert any(n.name == "RollbackNode" for n in nodes)
    
    # 4. Perform Rollback
    response = await client.post(f"/api/v1/approvals/{approval_id}/rollback")
    assert response.status_code == 200
    assert response.json()["data"] is True
    
    # 5. Verify Rollback (Node should be gone)
    # Since we use hard delete in restore_snapshot
    result_after = await db_session.execute(stmt)
    nodes_after = result_after.scalars().all()
    assert not any(n.name == "RollbackNode" for n in nodes_after)
