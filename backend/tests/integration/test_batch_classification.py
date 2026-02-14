
import pytest
import json
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from sqlalchemy import select
from app.services.batch_classification_service import BatchClassificationService

# Suppress noisy logs
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
from app.models.content import ContentItem, ContentNodeRelation
from app.models.pyramid import Pyramid, PyramidNode

# Helper to mock async context manager
class AsyncContextManagerMock:
    def __init__(self, session):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_batch_classification_integration(db_session):
    # 1. Setup Data
    pyramid = Pyramid(id=uuid4(), name="Test Pyramid", description="Desc")
    db_session.add(pyramid)
    
    node = PyramidNode(
        id=uuid4(), 
        pyramid_id=pyramid.id, 
        name="AI Node", 
        description="Artificial Intelligence",
        level=1,
        path="/",
        sort_order=0
    )
    db_session.add(node)
    
    items = []
    for i in range(3):
        item = ContentItem(
            id=uuid4(),
            title=f"AI Article {i}",
            url=f"http://example.com/ai/{i}",
            content_text="This is an article about Artificial Intelligence and Machine Learning.",
            ai_processed=False
        )
        db_session.add(item)
        items.append(item)
        
    await db_session.commit()

    # Debug: Check items in DB
    result = await db_session.execute(select(ContentItem))
    all_items = result.scalars().all()
    print(f"DEBUG: All items in DB: {len(all_items)}")
    for item in all_items:
        print(f"DEBUG: Item {item.id} ai_processed={item.ai_processed}")
    
    # 2. Mock Dependencies
    mock_ai_response = {
        "summary": "This is a summary about AI.",
        "tags": ["AI", "ML"],
        "concepts": ["Artificial Intelligence", "Machine Learning"],
        "success": True
    }
    
    with patch("app.services.batch_classification_service.ai_service") as mock_ai_service, \
         patch("app.services.evolution_engine.VectorService") as MockVectorService, \
         patch("app.services.batch_classification_service.AsyncSessionLocal") as MockSessionLocal:
        
        # Setup AI Service Mock
        mock_ai_service.chat_completion = AsyncMock(return_value=json.dumps(mock_ai_response))
        mock_ai_service.generate_summary.return_value = {"summary": mock_ai_response["summary"]}
        mock_ai_service.generate_tags.return_value = mock_ai_response["tags"]
        mock_ai_service.extract_concepts.return_value = mock_ai_response["concepts"]
        
        # Setup Vector Service Mock
        mock_vs = MockVectorService.return_value
        mock_vs.upsert_content_vector = AsyncMock(return_value=None)
        mock_vs.search_similar_nodes = AsyncMock(return_value=[
            {"id": node.id, "distance": 0.1, "metadata": {"name": "AI Node"}}
        ])
        
        # Setup Session Mock to use our test db_session
        # The service calls: async with AsyncSessionLocal() as db:
        MockSessionLocal.return_value = AsyncContextManagerMock(db_session)
        
        # 3. Run Batch Classification
        service = BatchClassificationService()
        result = await service._execute_batch_classification(batch_size=10)
        
        # 4. Verify Results
        assert result["processed_count"] == 3
        assert result["success_count"] == 3
        
        # Verify Items Updated
        for item in items:
            await db_session.refresh(item)
            assert item.ai_processed is True
            assert item.summary == mock_ai_response["summary"]
            assert item.tags == mock_ai_response["tags"]
            assert item.concepts == mock_ai_response["concepts"]
            
            # Verify Linked to Node
            stmt = select(ContentNodeRelation).where(
                ContentNodeRelation.content_id == item.id,
                ContentNodeRelation.node_id == node.id
            )
            rel = (await db_session.execute(stmt)).scalar_one_or_none()
            assert rel is not None
            assert rel.source == "ai_auto"
