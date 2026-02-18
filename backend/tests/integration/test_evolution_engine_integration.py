import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from sqlalchemy import select

from app.services.evolution_engine import EvolutionEngine
from app.models.pyramid import Pyramid, PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.approval import Approval

@pytest.mark.asyncio
async def test_auto_classify_content(db_session):
    # 1. Setup Data
    pyramid = Pyramid(id=uuid4(), name="Test Pyramid", description="Desc")
    db_session.add(pyramid)
    
    node = PyramidNode(
        id=uuid4(), 
        pyramid_id=pyramid.id, 
        name="ML Node", 
        description="Machine Learning",
        level=1,
        path="/",
        sort_order=0
    )
    db_session.add(node)
    
    content = ContentItem(
        id=uuid4(), 
        title="Intro to ML", 
        url="http://example.com/ml", 
        summary="Basic ML concepts",
        concepts=["machine learning", "AI"]
    )
    db_session.add(content)
    await db_session.commit()
    
    # 2. Mock VectorService
    with patch("app.services.evolution_engine.VectorService") as MockVectorService:
        mock_vs = MockVectorService.return_value
        # upsert just returns None
        mock_vs.upsert_content_vector = AsyncMock(return_value=None)
        # search returns our node with low distance (high similarity)
        mock_vs.search_similar_nodes = AsyncMock(return_value=[
            {"id": node.id, "distance": 0.1, "metadata": {"name": "ML Node"}}
        ])
        
        # 3. Run Engine
        engine = EvolutionEngine(db_session)
        # Set threshold to be sure (default is 0.5, so 0.1 < 0.5 passes)
        linked_count = await engine.auto_classify_content(content)
        
        # 4. Verify
        assert linked_count == 1
        
        # Verify DB Link
        result = await db_session.execute(
            select(ContentNodeRelation).where(
                ContentNodeRelation.content_id == content.id,
                ContentNodeRelation.node_id == node.id
            )
        )
        link = result.scalar_one_or_none()
        assert link is not None
        assert link.source == "ai_auto"

@pytest.mark.asyncio
async def test_discover_clusters(db_session):
    # 1. Setup Data
    pyramid_id = uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid", description="Desc")
    db_session.add(pyramid)
    await db_session.commit()
    
    # Create 5 unlinked content items with same tag
    tag = "NewTopic"
    content_ids = []
    for i in range(5):
        c = ContentItem(
            id=uuid4(),
            title=f"Item {i}",
            url=f"http://example.com/{i}",
            tags=[tag]
        )
        db_session.add(c)
        content_ids.append(c.id)
    await db_session.commit()
    
    # 2. Mock VectorService
    with patch("app.services.evolution_engine.VectorService") as MockVectorService:
        mock_vs = MockVectorService.return_value
        
        # Mock search_similar_nodes to be stateful or check args
        # First call: check if cluster exists (limit=1). Return high distance (no match).
        # Second call: find parent (limit=1). Return some parent or None.
        
        async def side_effect(query_text, limit=5, threshold=0.0):
            if query_text == tag:
                # Check if this is the "check existing" call or "find parent" call?
                # The logic is:
                # 1. search_similar_nodes(tag, limit=1) -> check existing
                # 2. if not match -> search_similar_nodes(tag, limit=1) -> find parent
                # We can just return high distance for both, meaning no parent found either (root node)
                return [{"id": uuid4(), "distance": 0.8, "metadata": {}}]
            return []
            
        mock_vs.search_similar_nodes = AsyncMock(side_effect=side_effect)
        
        # 3. Run Engine
        engine = EvolutionEngine(db_session)
        await engine.discover_clusters(pyramid_id)
        
        # 4. Verify Approval Proposal
        result = await db_session.execute(
            select(Approval).where(
                Approval.type == "create_node",
                Approval.status == "pending"
            )
        )
        proposals = result.scalars().all()
        assert len(proposals) == 1
        p = proposals[0]
        assert p.data["name"] == tag
        assert p.reason.startswith(f"Discovered topic cluster '{tag}'")
        # Check content_ids in proposal data are subset of our created contents
        prop_cids = p.data["content_ids"]
        for cid in prop_cids:
            assert str(cid) in [str(id) for id in content_ids]
