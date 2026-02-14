
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_input_processing_flow(client: AsyncClient, db_session: AsyncSession):
    # Setup Pyramid
    response = await client.post(
        "/api/v1/pyramids", 
        json={"name": "Input Test Pyramid", "description": "For Input Test"}
    )
    assert response.status_code == 201
    pyramid_id = response.json()["data"]["id"]

    # 1. Submit Text
    response = await client.post(
        "/api/v1/contents/text", 
        json={
            "text": "AI is the future.",
            "title": "Future of AI",
            "submitter_id": "user123"
        }
    )
    assert response.status_code == 200
    content_data = response.json()["data"]
    content_id = content_data["id"]

    # Verify Contribution created
    response = await client.get("/api/v1/contributions/")
    assert response.status_code == 200
    contributions = response.json()
    # Check if our contribution exists
    # Note: response is list of contributions directly (List[ContributionResponse])
    assert any(c["original_input"] == "AI is the future." for c in contributions)

    # 2. Analyze (Mocked)
    with patch("app.services.content_analyzer.ContentAnalyzer.analyze_content") as mock_analyze:
        mock_analyze.return_value = [
            {
                "id": str(uuid.uuid4()),
                "type": "create_node",
                "status": "pending",
                "data": {"name": "AI", "pyramid_id": pyramid_id},
                "source_content_id": content_id,
                    "pyramid_id": pyramid_id,
                    "confidence_score": 0.9,
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "reviewer_id": None,
                    "review_comment": None,
                    "review_comments": []
                }
            ]
        
        response = await client.post(
            f"/api/v1/contents/{content_id}/analyze",
            json={"pyramid_id": pyramid_id}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["type"] == "create_node"
