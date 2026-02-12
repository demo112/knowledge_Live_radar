import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch, AsyncMock, MagicMock
import uuid
from datetime import datetime

@pytest.mark.asyncio
async def test_upload_file():
    with patch("app.routers.contents.InputProcessor") as MockProcessor:
        mock_instance = MockProcessor.return_value
        content_id = uuid.uuid4()
        mock_instance.process_file_input = AsyncMock(return_value={
            "id": content_id,
            "title": "Test File",
            "url": "file://test.txt",
            "status": "pending",
            "created_at": datetime.now()
        })
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Create a dummy file for upload
            files = {'file': ('test.txt', b'test content', 'text/plain')}
            response = await ac.post("/api/v1/contents/upload", files=files, data={"submitter_id": "user123"})
            
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "Test File"
        assert data["status"] == "pending"
        mock_instance.process_file_input.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_content():
    content_id = str(uuid.uuid4())
    pyramid_id = str(uuid.uuid4())
    
    with patch("app.routers.contents.ContentAnalyzer") as MockAnalyzer:
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze_content = AsyncMock(return_value=[
            {
                "id": str(uuid.uuid4()),
                "type": "create_node",
                "status": "pending",
                "data": {"title": "New Node"},
                "pyramid_id": pyramid_id,
                "reviewer_id": None,
                "review_comment": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "applicant_id": "system",
                "source_content_id": content_id,
                "generated_by": "ai",
                "reason": "Analysis result",
                "confidence_score": 0.9,
                "target_id": None
            }
        ])
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                f"/api/v1/contents/{content_id}/analyze", 
                json={"pyramid_id": pyramid_id}
            )
            
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["type"] == "create_node"
        mock_instance.analyze_content.assert_called_once()

@pytest.mark.asyncio
async def test_execute_approval():
    approval_id = str(uuid.uuid4())
    
    with patch("app.routers.approvals.DecisionExecutor") as MockExecutor:
        mock_instance = MockExecutor.return_value
        mock_instance.execute_approval = AsyncMock(return_value=True)
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                f"/api/v1/approvals/{approval_id}/execute",
                params={"user_id": "admin"}
            )
            
        assert response.status_code == 200
        assert response.json()["data"] is True
        mock_instance.execute_approval.assert_called_once_with(uuid.UUID(approval_id), "admin")
