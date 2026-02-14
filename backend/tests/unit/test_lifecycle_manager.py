import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.lifecycle_manager import LifecycleManager
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from datetime import datetime
import uuid

@pytest.mark.asyncio
async def test_lifecycle_manager_success():
    manager = LifecycleManager()
    session = AsyncMock()
    session.add = MagicMock()
    
    source = InformationSource(id=uuid.uuid4(), error_count=2, status="ACTIVE")
    job = CrawlJob(status="COMPLETED", items_failed=0)
    
    await manager.update_source_status(source, job, session)
    
    assert source.error_count == 0
    assert source.status == "ACTIVE"
    assert source.last_crawled_at is not None
    session.add.assert_called_once()
    session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_lifecycle_manager_failure():
    manager = LifecycleManager()
    session = AsyncMock()
    session.add = MagicMock()
    
    source = InformationSource(id=uuid.uuid4(), error_count=2, status="ACTIVE")
    job = CrawlJob(status="FAILED", error_message="Test Error", items_failed=0)
    
    await manager.update_source_status(source, job, session)
    
    assert source.error_count == 3
    assert source.status == "MONITORING"
    assert source.last_error_message == "Test Error"
    session.add.assert_called_once()
    session.commit.assert_called_once()
