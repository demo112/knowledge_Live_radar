import pytest
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.models.strategy_adjustment import StrategyAdjustment
from app.models.approval import Approval
from app.services.source_lifecycle_manager import SourceLifecycleManager
from sqlalchemy import select

@pytest.mark.asyncio
async def test_lifecycle_integration(db_session):
    # 1. Create a source in MONITORING state
    source = InformationSource(
        name="Test Source",
        type="RSS",
        url="http://example.com/rss",
        status="MONITORING",
        error_count=4 # 1 error away from ADJUSTING (threshold is 5)
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    # 2. Simulate failure
    manager = SourceLifecycleManager(db_session)
    await manager.on_crawl_failure(str(source.id), "Connection refused")
    
    # 3. Verify transition to ADJUSTING
    await db_session.refresh(source)
    assert source.status == "ADJUSTING"
    assert source.error_count == 5
    
    # 4. Verify proposal creation
    stmt = select(Approval).where(
        Approval.target_id == source.id,
        Approval.type == "strategy_adjustment"
    )
    result = await db_session.execute(stmt)
    proposal = result.scalar_one_or_none()
    assert proposal is not None
    assert proposal.status == "pending"
    
    stmt = select(StrategyAdjustment).where(StrategyAdjustment.source_id == source.id)
    result = await db_session.execute(stmt)
    adjustment = result.scalar_one_or_none()
    assert adjustment is not None
    assert adjustment.proposal_id == str(proposal.id)
