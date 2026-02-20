
import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from sqlalchemy import select
from app.models.knowledge import KnowledgeNode
from app.models.content import ContentItem, ContentKnowledgeRelation
from app.services.evolution_engine import EvolutionEngine
from app.services.knowledge_service import KnowledgeService

@pytest.mark.asyncio
async def test_auto_classify_knowledge_node(db_session):
    # Setup data first
    node_id = uuid4()
    node = KnowledgeNode(
        id=node_id,
        name="AI Cognitive Models",
        description="Study of artificial cognitive architectures",
        ai_model={"summary": "Deep learning and symbolic AI combination"},
        content_count=0
    )
    db_session.add(node)
    
    content_id = uuid4()
    content = ContentItem(
        id=content_id,
        title="New Cognitive Architecture",
        summary="A paper about AI cognitive models and deep learning",
        concepts=["AI", "Cognitive Science"],
        url="http://example.com/ai-cog"
    )
    db_session.add(content)
    await db_session.commit()

    # Mock VectorService
    with patch("app.services.evolution_engine.VectorService") as MockVectorService:
        mock_instance = MockVectorService.return_value
        
        # Setup async mocks
        mock_instance.upsert_content_vector = AsyncMock()
        
        async def mock_search(query_text, limit=3, node_type=None):
            assert node_type == "knowledge_node"
            return [{
                "id": node_id,
                "distance": 0.1, 
                "metadata": {"type": "knowledge_node", "name": "AI Cognitive Models"}
            }]
        mock_instance.search_similar_nodes = mock_search
        
        # Initialize Engine
        evolution_engine = EvolutionEngine(db_session)
        
        # Execute
        linked_count = await evolution_engine.auto_classify_content(content)
        
        # Verify
        assert linked_count == 1
        
        # Check DB
        stmt = select(ContentKnowledgeRelation).where(
            ContentKnowledgeRelation.node_id == node_id,
            ContentKnowledgeRelation.content_id == content_id
        )
        result = await db_session.execute(stmt)
        relation = result.scalar_one_or_none()
        
        assert relation is not None
        assert relation.source == "ai_auto"
        assert relation.confidence > 0.8
        
        # Check Node Stats
        # Refresh node from DB
        result = await db_session.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
        updated_node = result.scalar_one()
        assert updated_node.content_count == 1

@pytest.mark.asyncio
async def test_evolve_node_model(db_session):
    # Setup data
    node_id = uuid4()
    initial_model = {
        "definition": "Old Definition",
        "key_attributes": ["Attr1"],
        "related_concepts": ["Concept1"]
    }
    node = KnowledgeNode(
        id=node_id,
        name="Evolving Concept",
        description="A concept that changes",
        ai_model=initial_model,
        content_count=0
    )
    db_session.add(node)
    
    # Add linked content
    content1 = ContentItem(
        id=uuid4(),
        title="New Research 1",
        summary="Adds Attr2 to the concept",
        url="http://example.com/1"
    )
    db_session.add(content1)
    
    content2 = ContentItem(
        id=uuid4(),
        title="New Research 2",
        summary="Refines definition",
        url="http://example.com/2"
    )
    db_session.add(content2)
    
    await db_session.commit()
    
    # Create link
    ks = KnowledgeService(db_session)
    await ks.link_content(node_id, content1.id, "manual")
    await ks.link_content(node_id, content2.id, "manual")

    # Mock AI Facade
    evolved_model = {
        "definition": "New Definition",
        "key_attributes": ["Attr1", "Attr2"],
        "related_concepts": ["Concept1", "Concept2"]
    }
    
    # Also mock VectorService as it is initialized in EvolutionEngine
    with patch("app.services.evolution_engine.ai_facade") as mock_ai, \
         patch("app.services.evolution_engine.VectorService") as MockVectorService:
        
        mock_ai.evolve_cognitive_model = AsyncMock(return_value=evolved_model)
        
        # Execute
        engine = EvolutionEngine(db_session)
        success = await engine.evolve_node_model(node_id)
        
        # Verify
        assert success is True
        mock_ai.evolve_cognitive_model.assert_called_once()
        
        # Check arguments
        call_args = mock_ai.evolve_cognitive_model.call_args
        assert call_args[0][0] == initial_model
        assert len(call_args[0][1]) == 2 # 2 content items
        
        # Check DB update
        result = await db_session.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
        updated_node = result.scalar_one()
        assert updated_node.ai_model == evolved_model
