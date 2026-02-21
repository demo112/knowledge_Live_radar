import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.douyin_service import douyin_service

client = TestClient(app)

@pytest.mark.asyncio
async def test_douyin_stream_api():
    # Mock the convert_stream generator
    async def mock_generator(url):
        yield {"stage": "downloading", "progress": 10, "message": "Downloading..."}
        yield {"stage": "completed", "progress": 100, "data": {"video_info": {"title": "Test"}, "content": {}, "markdown": "MD"}}

    with patch.object(douyin_service, "convert_stream", side_effect=mock_generator) as mock_method:
        response = client.post(
            "/api/v1/tools/douyin/stream",
            json={"url": "https://v.douyin.com/abc/"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Verify stream content
        content = response.text
        assert "data: " in content
        assert "downloading" in content
        assert "completed" in content
        
        # Verify correct URL passed
        mock_method.assert_called_once_with("https://v.douyin.com/abc/")

@pytest.mark.asyncio
async def test_douyin_convert_api_with_mixed_text():
    # Mock the convert method (not stream)
    mock_response = {
        "video_info": {"title": "Test", "url": "https://v.douyin.com/abc/", "author": "A", "duration": 10},
        "content": {"summary": "Sum", "key_points": [], "full_text": "Txt"},
        "markdown": "# Test"
    }
    
    with patch.object(douyin_service, "convert", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_response
        
        response = client.post(
            "/api/v1/tools/douyin/convert",
            json={"url": "Check this out https://v.douyin.com/abc/ cool video"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["video_info"]["title"] == "Test"
        
        # Verify URL extraction happens in service, so controller just passes the raw text
        # But wait, the controller calls service.convert(request.url).
        # The extraction logic is inside service.convert/convert_stream.
        # So we verify that service.convert was called with the FULL text
        mock_method.assert_called_once_with("Check this out https://v.douyin.com/abc/ cool video")
