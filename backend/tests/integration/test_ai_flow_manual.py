import pytest
import pytest_asyncio
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.services.content_processor import ContentProcessor
from app.services.ai_service import AIService
from app.services.prompt_loader import prompt_loader
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
    # Load prompts (mocking file reading to avoid dependency on actual files if needed, 
    # but here we assume prompt_loader works with actual files or we skip if not critical)
    # For integration test, we want to test PromptManager -> DB interaction.
    # So we should let prompt_loader run if possible, or manually insert prompts.
    # Let's assume prompts are loaded or we manually insert them for stability.
    await prompt_loader.load_initial_prompts()
    
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
             patch("app.services.content_processor.ai_service") as mock_ai_service:
            
            # Setup Validator instances
            mock_hard_instance = MockHard.return_value
            mock_hard_instance.validate = AsyncMock(return_value=(True, {"hard": "pass"}))
            
            mock_soft_instance = MockSoft.return_value
            mock_soft_instance.validate = AsyncMock(return_value=(True, {"soft": "pass", "score": 85}))
            
            mock_cross_instance = MockCross.return_value
            mock_cross_instance.validate = AsyncMock(return_value=(True, {"cross": "pass"}))

            # We need to mock: validate_content_soft, generate_summary, generate_tags, extract_concepts
            
            mock_ai_service.validate_content_soft = AsyncMock(return_value={
                "score": 85, 
                "reason": "Good",
                "dimensions": {"info": 8}
            })
            mock_ai_service.generate_summary = AsyncMock(return_value={
                "summary": "AI Agents summary",
                "key_points": ["Point 1"]
            })
            mock_ai_service.generate_tags = AsyncMock(return_value=["AI", "Tech"])
            mock_ai_service.extract_concepts = AsyncMock(return_value=[{"name": "Agent", "type": "Concept"}])
            
            # Also need client for the check `if not ai_service.client` in soft_validator
            mock_ai_service.client = True 

            # 3. Action
            processor = ContentProcessor()
            job = await processor.process_source(source, db_session)
            
            # 4. Verify Job Status
            assert job.status == "COMPLETED"
            assert job.items_new == 1
                
            # 5. Verify Content Item
            from sqlalchemy import select
            stmt = select(ContentItem).where(ContentItem.source_id == source.id)
            result = await db_session.execute(stmt)
            content = result.scalar_one()
            
            assert content.title == "The Future of AI Agents"
            assert content.ai_processed is True
            assert content.summary == "AI Agents summary"
            assert "AI" in content.tags
            assert content.concepts[0]["name"] == "Agent"
            
            print("\n✅ Integration Test Passed: Content successfully processed with AI fields.")
