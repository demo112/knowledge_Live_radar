
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.fetchers.request_utils import RequestUtils, RateLimitException
from app.services.source_lifecycle_manager import SourceLifecycleManager
from app.services.content_processor import ContentProcessor
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_request_utils_random_headers():
    headers1 = RequestUtils.get_random_headers()
    headers2 = RequestUtils.get_random_headers()
    
    assert "User-Agent" in headers1
    assert "User-Agent" in headers2
    assert "Accept" in headers1

@pytest.mark.asyncio
async def test_rate_limit_handling():
    with patch("httpx.AsyncClient.request") as mock_request:
        # Mock 429 response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitException):
            await RequestUtils.fetch_url("http://example.com")

@pytest.mark.asyncio
async def test_content_processor_rate_limit(db_session):
    # Setup source
    source = InformationSource(
        name="Test Source",
        type="RSS",
        url="http://test.com/rss",
        check_interval=3600
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    # Mock crawl_engine to raise RateLimitException
    with patch("app.services.content_processor.crawl_engine.crawl_source") as mock_crawl:
        mock_crawl.side_effect = RateLimitException("Too many requests")
        
        processor = ContentProcessor()
        job = await processor.process_source(source, db_session)
        
        assert job.status == "RATE_LIMITED"
        assert "Too many requests" in job.error_message
        
        # Verify source was cooled down (last_crawled_at updated)
        await db_session.refresh(source)
        assert source.last_crawled_at is not None
        
        # Handle timezone awareness
        last_crawled = source.last_crawled_at
        if last_crawled.tzinfo is None:
            last_crawled = last_crawled.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        assert (now - last_crawled).total_seconds() < 10

