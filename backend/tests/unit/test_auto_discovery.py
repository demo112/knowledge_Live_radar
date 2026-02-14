import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auto_discovery import SourceDiscoveryService

@pytest.mark.asyncio
async def test_discover_from_url():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml" />
            </head>
            <body>
                <a href="https://example.com/feed">Feed</a>
            </body>
        </html>
        """
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        discovery = SourceDiscoveryService()
        results = await discovery.discover_from_url("https://example.com")
        
        assert len(results) >= 1
        # Check RSS link
        rss_result = next((r for r in results if r['url'] == "https://example.com/rss.xml"), None)
        assert rss_result is not None
        assert rss_result['type'] == 'rss'
        
        # Check heuristic link
        feed_result = next((r for r in results if r['url'] == "https://example.com/feed"), None)
        assert feed_result is not None
