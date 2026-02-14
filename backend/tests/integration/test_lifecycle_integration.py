
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
from app.services.content_processor import ContentProcessor

@pytest.mark.asyncio
async def test_content_processor_lifecycle_integration_success(db_session):
    # Setup
    source = InformationSource(
        name="Integration Source",
        type="RSS",
        url="http://example.com/rss",
        status="VERIFYING",
        trial_runs=2,
        trial_successes=2
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    processor = ContentProcessor()
    
    # Mock crawl_engine and validators
    with patch("app.services.content_processor.crawl_engine") as mock_crawl, \
         patch("app.services.content_processor.HardValidator") as MockHard, \
         patch("app.services.content_processor.SoftValidator") as MockSoft, \
         patch("app.services.content_processor.CrossValidator") as MockCross, \
         patch("app.services.content_processor.EvolutionEngine") as MockEvo, \
         patch("app.services.content_processor.ai_service") as mock_ai, \
         patch("app.services.content_processor.auto_discovery") as mock_ad:
         
        mock_crawl.crawl_source = AsyncMock(return_value=[{"title": "Test", "url": "http://example.com/1", "content": "text"}])
        
        # Validators return True
        instance_hard = MockHard.return_value
        instance_hard.validate = AsyncMock(return_value=(True, {}))
        
        instance_soft = MockSoft.return_value
        instance_soft.validate = AsyncMock(return_value=(True, {"score": 90}))
        
        instance_cross = MockCross.return_value
        instance_cross.validate = AsyncMock(return_value=(True, {}))
        
        instance_evo = MockEvo.return_value
        instance_evo.auto_classify_content = AsyncMock(return_value=0)
        
        mock_ai.generate_summary = AsyncMock(return_value={"summary": "sum"})
        mock_ai.generate_tags = AsyncMock(return_value=[])
        mock_ai.extract_concepts = AsyncMock(return_value=[])
        
        mock_ad.process_content_links = AsyncMock()

        # Execute
        await processor.process_source(source, db_session)
        
        # Verify Lifecycle Manager was called (indirectly via state change)
        await db_session.refresh(source)
        # 2 existing + 1 new success = 3 -> Should become ACTIVE
        assert source.status == "ACTIVE"
        assert source.trial_successes == 3

@pytest.mark.asyncio
async def test_content_processor_lifecycle_integration_failure(db_session):
    # Setup
    source = InformationSource(
        name="Integration Source Fail",
        type="RSS",
        url="http://example.com/rss",
        status="ACTIVE",
        error_count=2
    )
    db_session.add(source)
    await db_session.commit()
    
    processor = ContentProcessor()
    
    # Mock crawl_engine to raise exception
    with patch("app.services.content_processor.crawl_engine") as mock_crawl:
        mock_crawl.crawl_source = AsyncMock(side_effect=Exception("Crawl failed"))
        
        # Execute
        await processor.process_source(source, db_session)
        
        # Verify Lifecycle Manager was called (indirectly via state change)
        await db_session.refresh(source)
        # 2 existing + 1 new error = 3 -> Should become MONITORING
        assert source.status == "MONITORING"
        assert source.error_count == 3
