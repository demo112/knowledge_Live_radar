import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.scheduler import CrawlScheduler
from app.models.source import InformationSource
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_check_sources():
    # Mock AsyncSessionLocal context manager
    mock_session = AsyncMock()
    mock_session_cls = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_session_cls.return_value.__aenter__.return_value = mock_session
    
    with patch("app.services.scheduler.AsyncSessionLocal", mock_session_cls), \
         patch("app.services.scheduler.content_processor.process_source") as mock_process, \
         patch("app.services.scheduler.lifecycle_manager.update_source_status") as mock_update:
        
        scheduler = CrawlScheduler()
        
        # Setup source due for crawl
        source = InformationSource(
            id="1", 
            status="ACTIVE", 
            check_interval=60, 
            last_crawled_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            name="Test Source"
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [source]
        mock_session.execute.return_value = mock_result
        
        await scheduler.check_sources()
        
        mock_process.assert_called_once()
        mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_check_sources_not_due():
    # Mock AsyncSessionLocal context manager
    mock_session = AsyncMock()
    mock_session_cls = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_session_cls.return_value.__aenter__.return_value = mock_session
    
    with patch("app.services.scheduler.AsyncSessionLocal", mock_session_cls), \
         patch("app.services.scheduler.content_processor.process_source") as mock_process:
        
        scheduler = CrawlScheduler()
        
        # Setup source NOT due for crawl
        source = InformationSource(
            id="1", 
            status="ACTIVE", 
            check_interval=3600, 
            last_crawled_at=datetime.now(timezone.utc), # Just crawled
            name="Test Source"
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [source]
        mock_session.execute.return_value = mock_result
        
        await scheduler.check_sources()
        
        mock_process.assert_not_called()
