import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.content_processor import ContentProcessor
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob
import uuid
from datetime import datetime

# Strategy for generating crawl items
crawl_item_strategy = st.fixed_dictionaries({
    "url": st.text(min_size=1),
    "title": st.text(min_size=1),
    "content": st.text(min_size=1),
    "published_at": st.datetimes()
})

@pytest.mark.asyncio
@given(items=st.lists(crawl_item_strategy, min_size=1, max_size=5))
@settings(max_examples=10)
async def test_auto_classification_invariants(items):
    with patch("app.services.content_processor.crawl_engine.crawl_source") as mock_crawl, \
         patch("app.services.content_processor.HardValidator") as MockHard, \
         patch("app.services.content_processor.SoftValidator") as MockSoft, \
         patch("app.services.content_processor.CrossValidator") as MockCross, \
         patch("app.services.content_processor.EvolutionEngine") as MockEvolution, \
         patch("app.services.content_processor.auto_discovery") as mock_discovery, \
         patch("app.services.content_processor.ai_service") as mock_ai:
         
        # Setup mocks
        mock_crawl.return_value = items
        
        MockHard.return_value.validate = AsyncMock(return_value=(True, {}))
        MockSoft.return_value.validate = AsyncMock(return_value=(True, {}))
        MockCross.return_value.validate = AsyncMock(return_value=(True, {}))
        
        mock_discovery.process_content_links = AsyncMock()
        
        mock_ai.generate_summary = AsyncMock(return_value={"summary": "summary"})
        mock_ai.generate_tags = AsyncMock(return_value=["tag"])
        mock_ai.extract_concepts = AsyncMock(return_value=["concept"])
        
        evolution_engine = MockEvolution.return_value
        # Simulate success: returns 1 linked node
        evolution_engine.auto_classify_content = AsyncMock(return_value=1)
        
        processor = ContentProcessor()
        session = AsyncMock()
        session.add = MagicMock()
        
        source = InformationSource(id=uuid.uuid4(), name="Test Source", type="rss", url="http://rss.com")
        
        job = await processor.process_source(source, session)
        
        # Invariant: Job completes
        assert job.status == "COMPLETED"
        # Invariant: Classified count should match items count (since all succeed)
        assert job.items_classified == len(items)
        assert job.items_classified <= job.items_new
        
        if len(items) > 0:
            assert evolution_engine.auto_classify_content.call_count == len(items)

@pytest.mark.asyncio
async def test_auto_classification_error_resilience():
    # Test specifically for error resilience
    with patch("app.services.content_processor.crawl_engine.crawl_source") as mock_crawl, \
         patch("app.services.content_processor.HardValidator") as MockHard, \
         patch("app.services.content_processor.SoftValidator") as MockSoft, \
         patch("app.services.content_processor.CrossValidator") as MockCross, \
         patch("app.services.content_processor.EvolutionEngine") as MockEvolution, \
         patch("app.services.content_processor.auto_discovery") as mock_discovery, \
         patch("app.services.content_processor.ai_service") as mock_ai:
         
        mock_crawl.return_value = [{"url": "http://test.com", "title": "Test", "content": "Content"}]
        MockHard.return_value.validate = AsyncMock(return_value=(True, {}))
        MockSoft.return_value.validate = AsyncMock(return_value=(True, {}))
        MockCross.return_value.validate = AsyncMock(return_value=(True, {}))
        mock_discovery.process_content_links = AsyncMock()
        mock_ai.generate_summary = AsyncMock(return_value={"summary": "summary"})
        mock_ai.generate_tags = AsyncMock(return_value=["tag"])
        mock_ai.extract_concepts = AsyncMock(return_value=["concept"])
        
        evolution_engine = MockEvolution.return_value
        evolution_engine.auto_classify_content = AsyncMock(side_effect=Exception("Error"))
        
        processor = ContentProcessor()
        session = AsyncMock()
        session.add = MagicMock()
        source = InformationSource(id=uuid.uuid4(), name="Test Source", type="rss", url="http://rss.com")
        
        job = await processor.process_source(source, session)
        
        # Invariant: Job still completes even if classification fails
        assert job.status == "COMPLETED"
        assert job.items_classified == 0
        evolution_engine.auto_classify_content.assert_called_once()
