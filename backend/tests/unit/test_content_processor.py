import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.content_processor import ContentProcessor
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from datetime import datetime, timezone
import uuid

@pytest.mark.asyncio
async def test_process_source():
    # Mock dependencies
    with patch("app.services.content_processor.crawl_engine.crawl_source") as mock_crawl, \
         patch("app.services.content_processor.HardValidator") as MockHard, \
         patch("app.services.content_processor.SoftValidator") as MockSoft, \
         patch("app.services.content_processor.CrossValidator") as MockCross:
        
        # Setup mocks
        mock_crawl.return_value = [{"url": "http://test.com", "title": "Test", "content": "Content"}]
        
        mock_hard = MockHard.return_value
        mock_hard.validate = AsyncMock(return_value=(True, {}))
        
        mock_soft = MockSoft.return_value
        mock_soft.validate = AsyncMock(return_value=(True, {}))
        
        mock_cross = MockCross.return_value
        mock_cross.validate = AsyncMock(return_value=(True, {}))
        
        # Setup session
        session = AsyncMock()
        session.add = MagicMock() # session.add is synchronous
        
        processor = ContentProcessor()
        source = InformationSource(id=uuid.uuid4(), name="Test Source", type="rss", url="http://rss.com")
        
        job = await processor.process_source(source, session)
        
        # Assertions
        assert session.add.call_count >= 3 
        assert session.commit.call_count >= 2
        
        assert job.status == "COMPLETED"
        assert job.items_new == 1
