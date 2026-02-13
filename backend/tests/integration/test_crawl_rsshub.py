import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.source import InformationSource
from app.services.crawl_engine import CrawlEngine

@pytest.mark.asyncio
async def test_crawl_rsshub_source():
    # Setup
    source = InformationSource(
        id=uuid.uuid4(),
        name="Test Bilibili",
        type="BILIBILI_USER",
        url="123456",
        config={}
    )
    
    # Mock httpx used by RSSFetcher (parent of RSSHubFetcher)
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = """
        <rss version="2.0">
        <channel>
            <title>Bilibili User</title>
            <item><title>Video 1</title><link>http://bilibili.com/video/1</link><description>Desc 1</description></item>
        </channel>
        </rss>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        engine = CrawlEngine()
        items = await engine.crawl_source(source)
        
        # Verify
        assert len(items) == 1
        assert items[0]["title"] == "Video 1"
        
        # Verify URL was converted
        # The call to httpx.get should use the RSSHub URL
        call_args = mock_get.call_args
        assert "rsshub.app/bilibili/user/video/123456" in call_args[0][0]
