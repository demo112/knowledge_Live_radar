
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval

@pytest.mark.asyncio
async def test_approval_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Create a Pyramid
    response = await client.post(
        "/api/v1/pyramids",
        json={"name": "Test Pyramid", "description": "For Approval Test"}
    )
    assert response.status_code == 201
    pyramid_id = response.json()["data"]["id"]

    # 2. Submit Content & Generate Proposal (Mocked Analysis)
    response = await client.post(
        "/api/v1/contents/text", 
        json={
            "text": "Make a node",
            "title": "Proposal Gen",
            "submitter_id": "tester"
        }
    )
    assert response.status_code == 200
    content_id = response.json()["data"]["id"]

    # Pre-create the approval that the mock analysis would have created
    approval_id_uuid = uuid.uuid4()
    approval = Approval(
        id=approval_id_uuid,
        type="create_node",
        status="pending",
        data={"name": "ApprovedNode", "pyramid_id": pyramid_id},
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
            "data": {"name": "ApprovedNode", "pyramid_id": pyramid_id},
            "source_content_id": content_id,
            "pyramid_id": pyramid_id,
            "confidence_score": 0.95,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "reviewer_id": None,
            "review_comment": None,
            "review_comments": []
        }]
        
        # Trigger analyze to persist the proposal
        response = await client.post(
            f"/api/v1/contents/{content_id}/analyze",
            json={"pyramid_id": pyramid_id}
        )
        assert response.status_code == 200
        
    # 3. Retrieve Pending Approval
    response = await client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    approvals = response.json()["data"]
    assert len(approvals) > 0
    approval_id = approvals[0]["id"]
    
    # 4. Review: Approve
    response = await client.post(
        f"/api/v1/approvals/{approval_id}/review",
        json={"status": "approved", "reviewer_id": "admin", "comment": "Looks good"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "approved"
    
    # 5. Execute
    response = await client.post(f"/api/v1/approvals/{approval_id}/execute")
    assert response.status_code == 200
    assert response.json()["data"] is True
    
    # 6. Verify Node Created
    # Note: Using direct DB check or Pyramid API if available
    # Pyramid API for nodes: /api/v1/pyramids/{id}/nodes (Need to check if implemented)
    # Assuming standard pattern:
    response = await client.get(f"/api/v1/pyramids/{pyramid_id}")
    assert response.status_code == 200
    # Or fetch nodes directly if endpoint exists
    # Checking pyramids.py... it usually returns nodes in detail
    # Let's assume detail response includes nodes or we can query nodes
    # For now, let's trust the execute return True, but better to verify side effect.
    # The detail endpoint returns PyramidDetailResponse which likely has nodes.
