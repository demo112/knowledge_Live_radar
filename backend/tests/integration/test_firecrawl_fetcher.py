import pytest
from unittest.mock import MagicMock, patch
from app.services.fetchers.firecrawl_fetcher import FirecrawlFetcher

@pytest.mark.asyncio
async def test_firecrawl_fetcher_fetch_mock():
    with patch("app.services.fetchers.firecrawl_fetcher.FirecrawlApp") as MockApp:
        mock_instance = MockApp.return_value
        # Mock .scrape instead of .scrape_url
        mock_instance.scrape.return_value = {
            "markdown": "# Test Content",
            "metadata": {"title": "Test Title", "sourceURL": "http://example.com"}
        }
        
        fetcher = FirecrawlFetcher()
        results = await fetcher.fetch("http://example.com")
        
        assert len(results) == 1
        assert results[0]["title"] == "Test Title"
        assert results[0]["content"] == "# Test Content"
        mock_instance.scrape.assert_called_once()

@pytest.mark.asyncio
async def test_firecrawl_fetcher_validate_mock():
    with patch("app.services.fetchers.firecrawl_fetcher.FirecrawlApp") as MockApp:
        mock_instance = MockApp.return_value
        mock_instance.scrape.return_value = {"markdown": "ok"}
        
        fetcher = FirecrawlFetcher()
        is_valid = await fetcher.validate_source("http://example.com")
        assert is_valid is True

@pytest.mark.asyncio
async def test_firecrawl_fetcher_validate_fail_mock():
    with patch("app.services.fetchers.firecrawl_fetcher.FirecrawlApp") as MockApp:
        mock_instance = MockApp.return_value
        mock_instance.scrape.side_effect = Exception("Failed")
        
        fetcher = FirecrawlFetcher()
        is_valid = await fetcher.validate_source("http://example.com")
        assert is_valid is False
