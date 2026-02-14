import pytest
import uuid
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.models.approval import Approval
from app.models.strategy_adjustment import StrategyAdjustment
from app.services.lifecycle_manager import LifecycleManager, SourceStatus

@pytest.mark.asyncio
async def test_lifecycle_transitions(db_session):
    manager = LifecycleManager()
    
    # 1. Setup Source (ACTIVE)
    source = InformationSource(
        id=uuid.uuid4(),
        name="Test Source",
        type="RSS",
        url="http://example.com",
        status=SourceStatus.ACTIVE,
        error_count=0
    )
    db_session.add(source)
    await db_session.commit()

    # 2. Test ACTIVE -> MONITORING (3 errors)
    job_fail = CrawlJob(status="FAILED", error_message="Error")
    
    # Error 1
    await manager.update_source_status(source, job_fail, db_session)
    assert source.error_count == 1
    assert source.status == SourceStatus.ACTIVE
    
    # Error 2
    await manager.update_source_status(source, job_fail, db_session)
    assert source.error_count == 2
    assert source.status == SourceStatus.ACTIVE
    
    # Error 3 -> MONITORING
    await manager.update_source_status(source, job_fail, db_session)
    assert source.error_count == 3
    assert source.status == SourceStatus.MONITORING
    
    # 3. Test MONITORING -> ADJUSTING (10 errors)
    source.error_count = 9
    await manager.update_source_status(source, job_fail, db_session)
    assert source.error_count == 10
    assert source.status == SourceStatus.ADJUSTING
    
    # Check if Proposal created
    # Need to query Approval table
    # But db_session might not have flushed fully if not committed in test?
    # The manager calls commit() at end of update_source_status
    
    # Use a new session or refresh to check DB
    # (Since we passed db_session, it should be committed)
    
    # Let's verify via query
    from sqlalchemy import select
    stmt = select(Approval).where(Approval.target_id == source.id)
    result = await db_session.execute(stmt)
    approval = result.scalars().first()
    
    assert approval is not None
    assert approval.type == "strategy_adjustment"
    assert approval.status == "pending"
    
    stmt_adj = select(StrategyAdjustment).where(StrategyAdjustment.source_id == source.id)
    result_adj = await db_session.execute(stmt_adj)
    adjustment = result_adj.scalars().first()
    
    assert adjustment is not None
    assert adjustment.proposal_id == str(approval.id)

    # 4. Test Recovery (ADJUSTING -> ACTIVE)
    job_success = CrawlJob(status="COMPLETED")
    await manager.update_source_status(source, job_success, db_session)
    
    assert source.status == SourceStatus.ACTIVE
    assert source.error_count == 0
    assert source.last_error_message is None

@pytest.mark.asyncio
async def test_check_monitoring_sources(db_session):
    manager = LifecycleManager()
    
    # Setup Source in MONITORING
    source = InformationSource(
        id=uuid.uuid4(),
        name="Monitoring Source",
        type="RSS",
        url="http://example.com/monitor",
        status=SourceStatus.MONITORING,
        error_count=5
    )
    db_session.add(source)
    await db_session.commit()
    
    # Mock crawl_engine.validate_source
    with patch("app.services.lifecycle_manager.crawl_engine.validate_source", new_callable=AsyncMock) as mock_validate:
        # Case 1: Reachable -> Log only (no change yet)
        mock_validate.return_value = True
        await manager.check_monitoring_sources(db_session)
        await db_session.refresh(source)
        assert source.status == SourceStatus.MONITORING
        assert source.error_count == 5 # No change
        
        # Case 2: Unreachable -> Error count ++
        mock_validate.return_value = False
        await manager.check_monitoring_sources(db_session)
        await db_session.refresh(source)
        assert source.error_count == 6
        
        # Case 3: Unreachable until threshold -> ADJUSTING
        source.error_count = 9
        await db_session.commit()
        
        mock_validate.return_value = False
        await manager.check_monitoring_sources(db_session)
        await db_session.refresh(source)
        
        assert source.error_count == 10
        assert source.status == SourceStatus.ADJUSTING
        
        # Verify proposal creation
        from sqlalchemy import select
        stmt = select(Approval).where(Approval.target_id == source.id)
        result = await db_session.execute(stmt)
        approval = result.scalars().first()
        assert approval is not None
