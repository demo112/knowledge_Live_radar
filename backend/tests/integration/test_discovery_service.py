
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4, UUID
from app.services.discovery_service import DiscoveryService
from app.schemas.knowledge import KnowledgeNodeCreate
from app.services.knowledge_service import KnowledgeService
from app.models.content import ContentItem

@pytest.mark.asyncio
async def test_discover_node_relations(db_session):
    # 1. Setup KnowledgeService and create two nodes
    knowledge_service = KnowledgeService(db_session)
    
    node1_data = KnowledgeNodeCreate(name="Node A", description="Description A", node_type="concept")
    node1 = await knowledge_service.create_node(node1_data)
    
    node2_data = KnowledgeNodeCreate(name="Node B", description="Description B", node_type="concept")
    node2 = await knowledge_service.create_node(node2_data)

    # 2. Mock VectorService
    with patch("app.services.discovery_service.VectorService") as MockVectorService:
        mock_vector_service = MockVectorService.return_value
        
        # Setup mock behavior for search_similar_nodes
        # When searching for Node A, return Node B as a result
        # Note: VectorService returns list of dicts
        mock_vector_service.search_similar_nodes = AsyncMock(return_value=[
            {"id": str(node2.id), "distance": 0.1, "metadata": {"name": "Node B"}}
        ])
        
        # 3. Instantiate DiscoveryService (it will use the mock)
        discovery_service = DiscoveryService(db_session)
        
        # 4. Call discover_node_relations
        relations = await discovery_service.discover_node_relations(node_id=node1.id, limit=5, threshold=0.5)
        
        # 5. Assertions
        assert len(relations) == 1
        assert relations[0]["target_node_id"] == node2.id
        assert relations[0]["source_node_id"] == node1.id
        
        # Verify search was called with correct text
        expected_query = f"{node1.name}: {node1.description}"
        mock_vector_service.search_similar_nodes.assert_called_once()
        args, kwargs = mock_vector_service.search_similar_nodes.call_args
        assert args[0] == expected_query

@pytest.mark.asyncio
async def test_discover_content_clusters(db_session):
    # 1. Setup - Create unlinked ContentItems
    c1 = ContentItem(
        id=uuid4(), title="Content 1", content_text="Text about AI", 
        url="http://example.com/1", status="pending", source_id=uuid4()
    )
    c2 = ContentItem(
        id=uuid4(), title="Content 2", content_text="Another text about AI", 
        url="http://example.com/2", status="pending", source_id=uuid4()
    )
    c3 = ContentItem(
        id=uuid4(), title="Content 3", content_text="Text about Cooking", 
        url="http://example.com/3", status="pending", source_id=uuid4()
    )
    c4 = ContentItem(
        id=uuid4(), title="Content 4", content_text="More AI text", 
        url="http://example.com/4", status="pending", source_id=uuid4()
    )
    
    db_session.add_all([c1, c2, c3, c4])
    await db_session.commit()
    
    # 2. Mock VectorService
    with patch("app.services.discovery_service.VectorService") as MockVectorService:
        mock_vector_service = MockVectorService.return_value
        
        # Setup mock behavior for get_content_embeddings
        # Return dict of vectors
        # c1, c2, c4 are similar. c3 is different.
        mock_vector_service.get_content_embeddings = AsyncMock(return_value={
            str(c1.id): [1.0, 0.0],
            str(c2.id): [0.9, 0.1],
            str(c3.id): [0.0, 1.0],
            str(c4.id): [0.95, 0.05]
        })
        
        # 3. Instantiate DiscoveryService
        discovery_service = DiscoveryService(db_session)
        
        # 4. Call discover_content_clusters
        clusters = await discovery_service.discover_content_clusters(batch_size=10, similarity_threshold=0.8)
        
        # 5. Assertions
        # Expect 1 cluster with c1, c2, c4 (size >= 3)
        # c3 is isolated or cluster size 1, so filtered out
        assert len(clusters) == 1
        
        cluster_item_ids = [item for item in clusters[0]["content_ids"]]
        assert c1.id in cluster_item_ids
        assert c2.id in cluster_item_ids
        assert c4.id in cluster_item_ids
        assert c3.id not in cluster_item_ids


        assert c3.id not in cluster_item_ids
