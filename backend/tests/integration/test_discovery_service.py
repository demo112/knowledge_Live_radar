import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.discovery_service import DiscoveryService
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeNodeCreate, KnowledgeNodeRelationCreate
from app.models.content import ContentItem
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_discover_node_relations(db_session: AsyncSession):
    # Setup
    ks = KnowledgeService(db_session)
    
    # Create nodes
    node1 = await ks.create_node(KnowledgeNodeCreate(name="Python", description="Programming Language"))
    node2 = await ks.create_node(KnowledgeNodeCreate(name="FastAPI", description="Web Framework for Python"))
    node3 = await ks.create_node(KnowledgeNodeCreate(name="Java", description="Programming Language"))
    
    # Create existing relation
    await ks.create_relation(node1.id, KnowledgeNodeRelationCreate(
        target_node_id=node3.id,
        relation_type="similar_to"
    ))
    
    # Mock VectorService
    with patch("app.services.discovery_service.VectorService") as MockVectorService:
        mock_vector = MockVectorService.return_value
        
        # We need to ensure the mock is async if the real method is async
        mock_vector.search_similar_nodes = AsyncMock()
        
        # Mock search results
        mock_vector.search_similar_nodes.return_value = [
            {"id": node2.id, "distance": 0.1, "metadata": {"name": "FastAPI"}}, # High similarity
            {"id": node3.id, "distance": 0.2, "metadata": {"name": "Java"}},    # Already related
            {"id": uuid4(), "distance": 2.0, "metadata": {"name": "Rust"}},     # Low similarity
        ]
        
        # Initialize DiscoveryService
        ds = DiscoveryService(db_session)
        ds.vector_service = mock_vector 
        
        # Discover relations for node1
        relations = await ds.discover_node_relations(node1.id, threshold=0.5)
        
        # Verify
        assert len(relations) == 1
        assert relations[0]["target_node_id"] == node2.id
        assert relations[0]["source_node_id"] == node1.id
        
        # Check that node3 was filtered out (existing relation)
        target_ids = [r["target_node_id"] for r in relations]
        assert node3.id not in target_ids

@pytest.mark.asyncio
async def test_discover_content_clusters(db_session: AsyncSession):
    # Setup
    ds = DiscoveryService(db_session)
    
    # Create unlinked content
    c1 = ContentItem(title="Python Basics", url="http://example.com/1", content_hash="hash1")
    c2 = ContentItem(title="Python Intro", url="http://example.com/2", content_hash="hash2")
    c3 = ContentItem(title="Java Intro", url="http://example.com/3", content_hash="hash3")
    c4 = ContentItem(title="Python Guide", url="http://example.com/4", content_hash="hash4")
    
    db_session.add_all([c1, c2, c3, c4])
    await db_session.commit()
    await db_session.refresh(c1)
    await db_session.refresh(c2)
    await db_session.refresh(c3)
    await db_session.refresh(c4)
    
    # Mock VectorService
    with patch("app.services.discovery_service.VectorService") as MockVectorService:
        mock_vector = MockVectorService.return_value
        
        # Mock embeddings: c1, c2, c4 are similar (Python), c3 is different (Java)
        # 2D vectors: [1, 0] vs [0, 1]
        # Python: [1, 0.1]
        # Java: [0.1, 1]
        
        embeddings_map = {
            c1.id: [1.0, 0.1],
            c2.id: [0.9, 0.2],
            c3.id: [0.1, 1.0],
            c4.id: [0.95, 0.15]
        }
        
        async def get_embeddings_side_effect(ids):
            return [embeddings_map[uid] for uid in ids]
            
        mock_vector.get_content_embeddings = AsyncMock(side_effect=get_embeddings_side_effect)
        
        # Manually set the instance
        ds.vector_service = mock_vector
        
        # Run discovery
        # Similarity threshold 0.8
        clusters = await ds.discover_content_clusters(batch_size=10, similarity_threshold=0.8)
        
        # Verify
        # Should find 1 cluster (Python) with size 3 (c1, c2, c4)
        # c3 is isolated
        assert len(clusters) == 1
        cluster = clusters[0]
        assert cluster["size"] == 3
        
        cluster_ids = set(cluster["content_ids"])
        assert c1.id in cluster_ids
        assert c2.id in cluster_ids
        assert c4.id in cluster_ids
        assert c3.id not in cluster_ids
