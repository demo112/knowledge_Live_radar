import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeNodeCreate
from app.models.content import ContentItem
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_evolve_node_model(db_session: AsyncSession):
    # Setup
    ks = KnowledgeService(db_session)
    
    # Create node
    node = await ks.create_node(KnowledgeNodeCreate(name="Python", description="Programming Language"))
    
    # Create content linked to node
    c1 = ContentItem(title="Python 3.11 Features", url="http://example.com/1", content_text="New features in Python 3.11...", content_hash="hash1")
    c2 = ContentItem(title="Asyncio in Python", url="http://example.com/2", content_text="How to use asyncio...", content_hash="hash2")
    
    db_session.add_all([c1, c2])
    await db_session.commit()
    await db_session.refresh(c1)
    await db_session.refresh(c2)
    
    # Link content
    await ks.link_content(node.id, c1.id)
    await ks.link_content(node.id, c2.id)
    
    # Mock AI Facade
    with patch("app.services.knowledge_service.ai_facade") as mock_ai:
        # Mock initial generation
        mock_ai.generate_cognitive_model = AsyncMock(return_value={
            "definition": "Python is a programming language.",
            "key_attributes": ["dynamic", "interpreted"],
            "related_concepts": [],
            "misconceptions": [],
            "evolution_path": []
        })
        
        # Mock evolution
        updated_model = {
            "definition": "Python is a versatile programming language with async support.",
            "key_attributes": ["dynamic", "interpreted", "asyncio"],
            "related_concepts": ["Concurrency"],
            "misconceptions": [],
            "evolution_path": ["Performance Optimization"]
        }
        mock_ai.evolve_cognitive_model = AsyncMock(return_value=updated_model)
        
        # 1. First call will generate model (since it's empty)
        # Note: In the implementation, if ai_model is empty, it calls generate_cognitive_model_for_node
        node = await ks.evolve_node_model(node.id)
        assert node.ai_model["definition"] == "Python is a programming language."
        
        # 2. Second call will evolve model
        node = await ks.evolve_node_model(node.id)
        assert node.ai_model["key_attributes"] == ["dynamic", "interpreted", "asyncio"]
        assert "Concurrency" in node.ai_model["related_concepts"]
