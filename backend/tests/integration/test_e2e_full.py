import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID
from app.services.intent_service import IntentService
from app.services.knowledge_service import KnowledgeService
from app.schemas.intent import IntentCreateRequest, IntentType, Action, ActionType, IntentParseResult
from app.schemas.knowledge import KnowledgeNodeCreate, KnowledgeClusterCreate
from app.models.knowledge import KnowledgeNode, KnowledgeCluster

@pytest.mark.asyncio
async def test_e2e_learn_intent_flow(db_session):
    """
    E2E Scenario: User wants to learn a new topic -> System creates cluster and nodes.
    """
    # 1. Setup Services
    intent_service = IntentService(db_session)
    knowledge_service = KnowledgeService(db_session)
    
    # 2. Mock AI Components (Intent Parsing & Action Generation)
    # We mock them to ensure deterministic behavior for the test
    
    mock_intent_result = IntentParseResult(
        original_text="I want to learn Rust",
        intent_type=IntentType.LEARN,
        primary_topic="Rust",
        goal="Learn Rust programming language",
        confidence=0.95,
        sub_topics=["Ownership", "Borrowing"]
    )
    
    mock_actions = [
        Action(
            type=ActionType.CREATE_CLUSTER, 
            description="Create Rust Cluster", 
            parameters={
                "name": "Rust", 
                "description": "Rust Knowledge Cluster",
                "center_node_name": "Rust"
            },
            priority=1
        ),
        Action(
            type=ActionType.CREATE_NODE, 
            description="Create Ownership Node", 
            parameters={
                "name": "Ownership", 
                "description": "Rust Ownership Concept",
                "node_type": "concept",
                "parent_name": "Rust"
            },
            priority=2
        ),
        Action(
            type=ActionType.CREATE_NODE, 
            description="Create Borrowing Node", 
            parameters={
                "name": "Borrowing", 
                "description": "Rust Borrowing Concept",
                "node_type": "concept",
                "parent_name": "Rust"
            },
            priority=2
        )
    ]

    with patch("app.services.intent_service.ai_facade.parse_intent", new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = mock_intent_result
        
        with patch("app.services.intent_service.action_generator.generate_actions", new_callable=AsyncMock) as mock_gen_actions:
            mock_gen_actions.return_value = mock_actions
            
            # 3. User Input (Trigger Intent)
            request = IntentCreateRequest(text="I want to learn Rust")
            response = await intent_service.process_intent(request)
            
            # Verify Intent Processing
            assert response.parsed_intent.intent_type == IntentType.LEARN
            assert len(response.suggested_actions) == 3
            
            # 4. Execute Actions (Simulate Execution Engine)
            # In a real system, this might be automated or user-confirmed. 
            # Here we manually execute the actions using KnowledgeService based on the plan.
            
            cluster_id = None
            center_node_id = None
            
            for action in response.suggested_actions:
                if action.type == ActionType.CREATE_CLUSTER:
                    # Create Cluster
                    params = action.parameters
                    cluster_data = KnowledgeClusterCreate(
                        name=params["name"],
                        description=params.get("description"),
                        center_node_id=None # Will create center node logic below
                    )
                    # For simplicity in this test, we create center node first if needed, 
                    # but KnowledgeService.create_cluster might not auto-create node yet.
                    # Let's create the center node "Rust" first.
                    
                    center_node = await knowledge_service.create_node(KnowledgeNodeCreate(
                        name=params["center_node_name"],
                        node_type="concept"
                    ))
                    center_node_id = center_node.id
                    
                    cluster_data.center_node_id = center_node.id
                    cluster = await knowledge_service.create_cluster(cluster_data)
                    cluster_id = cluster.id
                    
                    assert cluster.name == "Rust"
                    assert cluster.center_node_id == center_node.id
                    
                elif action.type == ActionType.CREATE_NODE:
                    # Create Node and Link to Parent
                    params = action.parameters
                    node_data = KnowledgeNodeCreate(
                        name=params["name"],
                        description=params.get("description"),
                        node_type=params.get("node_type", "concept")
                    )
                    node = await knowledge_service.create_node(node_data)
                    
                    # Link to Parent (Center Node)
                    # Assuming parent_name refers to center node for this test
                    if params.get("parent_name") == "Rust" and center_node_id:
                         from app.schemas.knowledge import KnowledgeNodeRelationCreate
                         await knowledge_service.create_relation(
                             center_node_id, 
                             KnowledgeNodeRelationCreate(
                                 target_node_id=node.id,
                                 relation_type="parent"
                             )
                         )
                         
                    # Add to Cluster
                    if cluster_id:
                        from app.schemas.knowledge import ClusterNodeMembershipCreate
                        await knowledge_service.add_node_to_cluster(
                            cluster_id,
                            ClusterNodeMembershipCreate(node_id=node.id)
                        )

            # 5. Verify Graph Structure
            # We expect: Rust -> Ownership, Rust -> Borrowing
            if center_node_id:
                graph = await knowledge_service.get_knowledge_graph(center_node_id, depth=1)
                
                node_names = {n.name for n in graph["nodes"]}
                assert "Rust" in node_names
                assert "Ownership" in node_names
                assert "Borrowing" in node_names
                
                assert len(graph["edges"]) == 2

@pytest.mark.asyncio
async def test_e2e_content_ingestion_flow(db_session):
    """
    E2E Scenario: Ingest content -> Classify (via Vector Search) -> Link to Node.
    """
    from app.services.input_processor import InputProcessor
    from app.services.knowledge_service import KnowledgeService
    from app.schemas.knowledge import KnowledgeNodeCreate
    from app.services.evolution_engine import EvolutionEngine
    from app.models.content import ContentKnowledgeRelation
    from sqlalchemy import select
    
    input_processor = InputProcessor(db_session)
    knowledge_service = KnowledgeService(db_session)
    
    # 1. Create a Node first (target for classification)
    node = await knowledge_service.create_node(KnowledgeNodeCreate(name="Ownership", node_type="concept"))
    
    # 2. Ingest Content
    content = await input_processor.process_text_input(
        text="Ownership is Rust's most unique feature...",
        title="Rust Ownership Explained"
    )
    
    # 3. Initialize EvolutionEngine with current session
    evolution_engine = EvolutionEngine(db_session)
    
    # 4. Mock Vector Service
    # We mock search_similar_nodes to return our node
    with patch.object(evolution_engine.vector_service, "search_similar_nodes", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"id": str(node.id), "distance": 0.1}] # Low distance = High similarity
        
        with patch.object(evolution_engine.vector_service, "upsert_content_vector", new_callable=AsyncMock):
             # 5. Trigger Auto Classification
             linked_count = await evolution_engine.auto_classify_content(content)
             
             assert linked_count == 1
             
             # 6. Verify Linkage
             # Query ContentKnowledgeRelation
             stmt = select(ContentKnowledgeRelation).where(
                 ContentKnowledgeRelation.node_id == node.id,
                 ContentKnowledgeRelation.content_id == content.id
             )
             result = await db_session.execute(stmt)
             relation = result.scalar_one_or_none()
             
             assert relation is not None
             assert relation.confidence > 0.8 # 1.0 - 0.1 = 0.9

@pytest.mark.asyncio
async def test_e2e_graph_query(db_session):
    """
    E2E Scenario: Create Graph -> Query Graph.
    """
    knowledge_service = KnowledgeService(db_session)
    
    # 1. Create Nodes
    root = await knowledge_service.create_node(KnowledgeNodeCreate(name="Root", node_type="concept"))
    child1 = await knowledge_service.create_node(KnowledgeNodeCreate(name="Child1", node_type="concept"))
    child2 = await knowledge_service.create_node(KnowledgeNodeCreate(name="Child2", node_type="concept"))
    grandchild = await knowledge_service.create_node(KnowledgeNodeCreate(name="GrandChild", node_type="concept"))
    
    # 2. Create Relations
    from app.schemas.knowledge import KnowledgeNodeRelationCreate
    
    # Root -> Child1
    await knowledge_service.create_relation(root.id, KnowledgeNodeRelationCreate(target_node_id=child1.id, relation_type="parent"))
    # Root -> Child2
    await knowledge_service.create_relation(root.id, KnowledgeNodeRelationCreate(target_node_id=child2.id, relation_type="parent"))
    # Child1 -> GrandChild
    await knowledge_service.create_relation(child1.id, KnowledgeNodeRelationCreate(target_node_id=grandchild.id, relation_type="parent"))
    
    # 3. Query Graph (Depth 2)
    # Should return Root, Child1, Child2, GrandChild
    graph = await knowledge_service.get_knowledge_graph(root.id, depth=2)
    
    node_names = {n.name for n in graph["nodes"]}
    assert "Root" in node_names
    assert "Child1" in node_names
    assert "Child2" in node_names
    assert "GrandChild" in node_names
    
    assert len(graph["nodes"]) == 4
    assert len(graph["edges"]) == 3
    
    # 4. Query Graph (Depth 1)
    # Should return Root, Child1, Child2
    graph_d1 = await knowledge_service.get_knowledge_graph(root.id, depth=1)
    
    node_names_d1 = {n.name for n in graph_d1["nodes"]}
    assert "Root" in node_names_d1
    assert "Child1" in node_names_d1
    assert "Child2" in node_names_d1
    assert "GrandChild" not in node_names_d1

@pytest.mark.asyncio
async def test_e2e_approval_flow(db_session):
    """
    E2E Scenario: AI Suggestion -> Human Approval -> Execution.
    """
    from app.services.suggestion_executor import SuggestionExecutor
    from app.models.ai_suggestion import AISuggestion
    from app.models.pyramid import Pyramid, PyramidNode
    from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
    from app.services.pyramid_service import PyramidService
    
    # 1. Setup Pyramid and Root Node
    pyramid_service = PyramidService(db_session)
    pyramid = await pyramid_service.create_pyramid(PyramidCreate(name="Approval Test Pyramid"))
    
    # Create root node directly via service to ensure proper init
    root_node = await pyramid_service.add_node(pyramid.id, PyramidNodeCreate(name="Root Node", level=0))
    
    # 2. Create AISuggestion (Pending)
    suggestion_id = uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        type="optimization",
        action_type="create_node",
        target_type="pyramid_node",
        pyramid_id=pyramid.id,
        params={
            "name": "Suggested Child",
            "parent_id": str(root_node.id),
            "description": "AI suggested this node"
        },
        reason="To expand the pyramid",
        status="pending",
        data={}, # Required field
        input_hash="test_hash_123" # Required field
    )
    db_session.add(suggestion)
    await db_session.commit()
    
    # 3. Approve Suggestion
    executor = SuggestionExecutor(db_session)
    
    # Mock notify_status_change to avoid external calls or complex setup
    with patch.object(executor, "_notify_status_change", new_callable=AsyncMock):
        approve_result = await executor.approve(str(suggestion_id), db_session)
        assert approve_result["success"] is True
        assert approve_result["data"]["status"] == "approved"
        
        # Verify status in DB
        await db_session.refresh(suggestion)
        assert suggestion.status == "approved"
        
        # 4. Execute Suggestion
        # Mock snapshot service to avoid complexity
        with patch.object(executor.snapshot_service, "create_snapshot", new_callable=AsyncMock):
             exec_result = await executor.execute(str(suggestion_id), db_session)
             assert exec_result["success"] is True
             
             # 5. Verify Execution (Node Created)
             await db_session.refresh(suggestion)
             assert suggestion.status == "executed"
             
             # Check if node exists
             # We can check pyramid nodes
             nodes = await pyramid_service.get_nodes(pyramid.id)
             node_names = {n.name for n in nodes}
             assert "Suggested Child" in node_names
