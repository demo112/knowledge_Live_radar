import pytest
import pytest_asyncio
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime

from app.services.content_processor import ContentProcessor
from app.core.ai.facade import ai_facade
from app.core.ai.prompt_loader import prompt_loader
from app.models.source import InformationSource
from app.models.content import ContentItem
from app.database import Base

# Mock data
MOCK_CONTENT = {
    "url": "http://example.com/ai-article",
    "title": "The Future of AI Agents",
    "content": "AI Agents are evolving rapidly. They can plan, reason, and execute tasks.",
    "published_at": datetime.now()
}

MOCK_AI_RESPONSES = {
    "soft_validation": '{"score": 85, "reason": "High quality technical content", "dimensions": {"info_density": 8, "logic": 9}}',
    "summary_generation": '{"summary": "This article discusses the rapid evolution of AI Agents.", "key_points": ["Planning", "Reasoning", "Execution"]}',
    "tag_generation": '{"tags": ["AI", "Agents", "Future"]}',
    "concept_extraction": '{"concepts": [{"name": "AI Agents", "type": "Technology"}]}'
}

@pytest.fixture
async def db_session():
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_ai_content_flow(db_session):
    """
    Integration Test: AI Content Processing Flow
    
    Steps:
    1. Setup: Load prompts, Create Source
    2. Mock: Crawl Engine & AI Service
    3. Action: Run ContentProcessor
    4. Verify: ContentItem created with AI fields
    """
    
    # 1. Setup
    # Prompts are loaded from files by prompt_loader, no need to load_initial_prompts
    
    source = InformationSource(
        name="Test Source",
        type="rss",
        url="http://example.com/rss",
        status="active",
        check_interval=60
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    
    # 2. Mocking
    with patch("app.services.content_processor.crawl_engine") as mock_crawl:
        mock_crawl.crawl_source = AsyncMock(return_value=[MOCK_CONTENT])
        
        # Mock Validators
        with patch("app.services.content_processor.HardValidator") as MockHard, \
             patch("app.services.content_processor.SoftValidator") as MockSoft, \
             patch("app.services.content_processor.CrossValidator") as MockCross, \
             patch("app.services.content_processor.EvolutionEngine") as MockEvolution, \
             patch("app.services.content_processor.ai_facade") as mock_ai_facade:
            
            # Setup Validator instances
            mock_hard_instance = MockHard.return_value
            mock_hard_instance.validate = AsyncMock(return_value=(True, {"hard": "pass"}))
            
            mock_soft_instance = MockSoft.return_value
            mock_soft_instance.validate = AsyncMock(return_value=(True, {"soft": "pass", "score": 85}))
            
            mock_cross_instance = MockCross.return_value
            mock_cross_instance.validate = AsyncMock(return_value=(True, {"cross": "pass"}))

            mock_evolution_instance = MockEvolution.return_value

            # We need to mock: validate_content_soft, generate_summary, generate_tags, extract_concepts
            
            mock_ai_facade.validate_content_soft = AsyncMock(return_value={
                "score": 85, 
                "reason": "Good",
                "dimensions": {"info": 8}
            })
            mock_ai_facade.generate_summary = AsyncMock(return_value={
                "summary": "AI Agents summary",
                "key_points": ["Point 1"]
            })
            mock_ai_facade.generate_tags = AsyncMock(return_value=["AI", "Agents"])
            mock_ai_facade.extract_concepts = AsyncMock(return_value=[{"name": "AI Agents", "type": "Tech"}])
            
            # 3. Action
            processor = ContentProcessor()
            job = await processor.process_source(source, db_session)
            
            # 4. Verify
            assert job.status == "COMPLETED"
            assert job.items_fetched == 1
            
            # Let's check the content created
            
            stmt = select(ContentItem).where(ContentItem.source_id == source.id)
            result = await db_session.execute(stmt)
            content_items = result.scalars().all()
            
            assert len(content_items) == 1
            item = content_items[0]
            assert item.title == "The Future of AI Agents"
            assert item.summary == "AI Agents summary"
            assert "AI" in item.tags
            assert item.ai_processed is True
