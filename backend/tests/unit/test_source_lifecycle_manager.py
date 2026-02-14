
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.source import InformationSource
from app.services.source_lifecycle_manager import SourceLifecycleManager

@pytest.mark.asyncio
async def test_verify_source_success(db_session):
    # Setup
    source = InformationSource(
        name="Test Source",
        type="RSS",
        url="http://example.com/rss",
        status="DISCOVERED"
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    manager = SourceLifecycleManager(db_session)
    
    # Mock crawl_engine
    with patch("app.services.source_lifecycle_manager.crawl_engine") as mock_crawl:
        mock_crawl.crawl_source = AsyncMock(return_value=[{"title": "Test Item"}])
        
        # Execute
        result = await manager.verify_source(str(source.id))
        
        # Verify
        assert result is True
        
        # Reload source
        await db_session.refresh(source)
        assert source.status == "VERIFYING"
        assert source.trial_runs == 0
        assert source.trial_successes == 0
        assert source.error_count == 0

@pytest.mark.asyncio
async def test_verify_source_failure(db_session):
    # Setup
    source = InformationSource(
        name="Test Source Fail",
        type="RSS",
        url="http://example.com/rss",
        status="DISCOVERED"
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    manager = SourceLifecycleManager(db_session)
    
    # Mock crawl_engine failure (empty list)
    with patch("app.services.source_lifecycle_manager.crawl_engine") as mock_crawl:
        mock_crawl.crawl_source = AsyncMock(return_value=[])
        
        # Execute
        result = await manager.verify_source(str(source.id))
        
        # Verify
        assert result is False
        
        # Reload source
        await db_session.refresh(source)
        assert source.status == "DISCOVERED" # Should stay discovered? Or error? Logic says only updates status on success
        assert source.error_count == 1
        assert "No items returned" in source.last_error_message

@pytest.mark.asyncio
async def test_trial_period_success(db_session):
    # Setup
    source = InformationSource(
        name="Test Trial",
        type="RSS",
        url="http://example.com/rss",
        status="VERIFYING",
        trial_runs=2,
        trial_successes=2
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    manager = SourceLifecycleManager(db_session)
    
    # Simulate success
    await manager.on_crawl_success(str(source.id))
    
    # Verify
    await db_session.refresh(source)
    assert source.trial_runs == 3
    assert source.trial_successes == 3
    assert source.status == "ACTIVE" # 3 consecutive successes

@pytest.mark.asyncio
async def test_error_transitions(db_session):
    # Setup
    source = InformationSource(
        name="Test Error",
        type="RSS",
        url="http://example.com/rss",
        status="ACTIVE",
        error_count=2
    )
    db_session.add(source)
    await db_session.commit()
    
    manager = SourceLifecycleManager(db_session)
    
    # 3rd failure -> MONITORING
    await manager.on_crawl_failure(str(source.id), "Error 3")
    await db_session.refresh(source)
    assert source.status == "MONITORING"
    assert source.error_count == 3
    
    # 4th failure -> Still MONITORING
    await manager.on_crawl_failure(str(source.id), "Error 4")
    await db_session.refresh(source)
    assert source.status == "MONITORING"
    assert source.error_count == 4
    
    # 5th failure -> ADJUSTING
    await manager.on_crawl_failure(str(source.id), "Error 5")
    await db_session.refresh(source)
    assert source.status == "ADJUSTING"
    assert source.error_count == 5
    
    # Skip to 9 failures
    source.error_count = 9
    await db_session.commit()
    
    # 10th failure -> DEAD
    await manager.on_crawl_failure(str(source.id), "Error 10")
    await db_session.refresh(source)
    assert source.status == "DEAD"

@pytest.mark.asyncio
async def test_recovery(db_session):
    # Setup
    source = InformationSource(
        name="Test Recovery",
        type="RSS",
        url="http://example.com/rss",
        status="MONITORING",
        recovery_count=2
    )
    db_session.add(source)
    await db_session.commit()
    
    manager = SourceLifecycleManager(db_session)
    
    # 3rd success -> ACTIVE
    await manager.on_crawl_success(str(source.id))
    await db_session.refresh(source)
    assert source.status == "ACTIVE"
    assert source.recovery_count == 0
