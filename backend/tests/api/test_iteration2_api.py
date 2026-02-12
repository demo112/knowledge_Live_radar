import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch, AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_crawl_source_manual():
    source_id = str(uuid.uuid4())
    with patch("app.routers.sources.SourceService") as MockService, \
         patch("app.routers.sources.content_processor") as mock_processor, \
         patch("app.routers.sources.lifecycle_manager") as mock_lifecycle:
         
        mock_service_instance = MockService.return_value
        mock_service_instance.get_source = AsyncMock(return_value=MagicMock(id=source_id))
        
        mock_job = MagicMock(id="job_id", status="COMPLETED", items_new=5)
        mock_processor.process_source = AsyncMock(return_value=mock_job)
        mock_lifecycle.update_source_status = AsyncMock()
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(f"/api/v1/sources/{source_id}/crawl")
            
        assert response.status_code == 200
        assert response.json()["data"]["items_new"] == 5

@pytest.mark.asyncio
async def test_discovery():
    with patch("app.routers.discovery.auto_discovery") as mock_discovery:
        mock_discovery.discover_from_url = AsyncMock(return_value=[
            {"title": "Test Feed", "url": "http://test.com/rss", "type": "rss"}
        ])
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/api/v1/discovery/discover", json={"url": "http://test.com"})
            
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["type"] == "rss"
