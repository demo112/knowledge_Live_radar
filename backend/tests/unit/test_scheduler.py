import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.scheduler.tasks import run_content_crawl
from app.models.source import InformationSource
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_run_content_crawl():
    # Mock AsyncSessionLocal context manager
    mock_session = AsyncMock()
    mock_session_cls = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_session_cls.return_value.__aenter__.return_value = mock_session
    
    with patch("app.services.scheduler.tasks.AsyncSessionLocal", mock_session_cls), \
         patch("app.services.scheduler.tasks.crawl_manager.add_task") as mock_add_task:
        
        # Setup source due for crawl
        source = InformationSource(
            id="1", 
            status="ACTIVE", 
            check_interval=60, 
            last_crawled_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            name="Test Source",
            is_deleted=False
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [source]
        mock_session.execute.return_value = mock_result
        
        await run_content_crawl()
        
        mock_add_task.assert_called_once_with(source.id, priority=1)

@pytest.mark.asyncio
async def test_run_content_crawl_not_due():
    # Mock AsyncSessionLocal context manager
    mock_session = AsyncMock()
    mock_session_cls = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_session_cls.return_value.__aenter__.return_value = mock_session
    
    with patch("app.services.scheduler.tasks.AsyncSessionLocal", mock_session_cls), \
         patch("app.services.scheduler.tasks.crawl_manager.add_task") as mock_add_task:
        
        # Setup source NOT due for crawl
        source = InformationSource(
            id="1", 
            status="ACTIVE", 
            check_interval=3600, 
            last_crawled_at=datetime.now(timezone.utc), # Just crawled
            name="Test Source",
            is_deleted=False
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [source]
        mock_session.execute.return_value = mock_result
        
        await run_content_crawl()
        
        mock_add_task.assert_not_called()
