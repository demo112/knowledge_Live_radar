import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.fetchers.rss import RSSFetcher
from app.services.fetchers.api import APIFetcher
from app.services.crawl_engine import CrawlEngine
from app.models.source import InformationSource

@pytest.mark.asyncio
async def test_rss_fetcher():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <item>
                <title>Test Item</title>
                <link>http://example.com/1</link>
                <description>Test Description</description>
            </item>
        </channel>
        </rss>
        """
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        fetcher = RSSFetcher()
        items = await fetcher.fetch("http://example.com/rss")
        
        assert len(items) == 1
        assert items[0]["title"] == "Test Item"
        assert items[0]["url"] == "http://example.com/1"

@pytest.mark.asyncio
async def test_api_fetcher():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"title": "Test API Item", "url": "http://example.com/api/1"}
        ]
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        fetcher = APIFetcher()
        items = await fetcher.fetch("http://example.com/api")
        
        assert len(items) == 1
        assert items[0]["title"] == "Test API Item"

@pytest.mark.asyncio
async def test_crawl_engine():
    with patch("app.services.crawl_engine.get_fetcher") as mock_get_fetcher:
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = [{"title": "Test"}]
        mock_get_fetcher.return_value = mock_fetcher
        
        engine = CrawlEngine()
        source = InformationSource(name="Test", type="rss", url="http://test.com")
        items = await engine.crawl_source(source)
        
        assert len(items) == 1
        assert items[0]["title"] == "Test"
