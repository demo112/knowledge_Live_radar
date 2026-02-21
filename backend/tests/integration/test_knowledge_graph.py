import pytest
from uuid import uuid4
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeNodeCreate, KnowledgeNodeRelationCreate

@pytest.mark.asyncio
async def test_get_knowledge_graph(db_session):
    service = KnowledgeService(db_session)
    
    # 1. Create a graph structure
    # A -> B -> C
    # |
    # -> D
    
    node_a = await service.create_node(KnowledgeNodeCreate(name="Node A", node_type="concept"))
    node_b = await service.create_node(KnowledgeNodeCreate(name="Node B", node_type="concept"))
    node_c = await service.create_node(KnowledgeNodeCreate(name="Node C", node_type="concept"))
    node_d = await service.create_node(KnowledgeNodeCreate(name="Node D", node_type="concept"))
    
    # A -> B
    await service.create_relation(node_a.id, KnowledgeNodeRelationCreate(target_node_id=node_b.id, relation_type="related"))
    # B -> C
    await service.create_relation(node_b.id, KnowledgeNodeRelationCreate(target_node_id=node_c.id, relation_type="related"))
    # A -> D
    await service.create_relation(node_a.id, KnowledgeNodeRelationCreate(target_node_id=node_d.id, relation_type="related"))
    
    # 2. Test Depth 1 (Should get A, B, D)
    graph_d1 = await service.get_knowledge_graph(node_a.id, depth=1)
    
    node_ids_d1 = {node.id for node in graph_d1["nodes"]}
    assert node_a.id in node_ids_d1
    assert node_b.id in node_ids_d1
    assert node_d.id in node_ids_d1
    assert node_c.id not in node_ids_d1
    
    # Edges should contain A->B and A->D
    edge_ids_d1 = {e.id for e in graph_d1["edges"]}
    assert len(edge_ids_d1) == 2
    
    # 3. Test Depth 2 (Should get A, B, C, D)
    graph_d2 = await service.get_knowledge_graph(node_a.id, depth=2)
    
    node_ids_d2 = {node.id for node in graph_d2["nodes"]}
    assert node_a.id in node_ids_d2
    assert node_b.id in node_ids_d2
    assert node_c.id in node_ids_d2
    assert node_d.id in node_ids_d2
    
    # Edges should contain A->B, A->D, B->C
    edge_ids_d2 = {e.id for e in graph_d2["edges"]}
    assert len(edge_ids_d2) == 3
    
    # 4. Test filtering by relation type
    # Add B -> E (type="parent")
    node_e = await service.create_node(KnowledgeNodeCreate(name="Node E", node_type="concept"))
    await service.create_relation(node_b.id, KnowledgeNodeRelationCreate(target_node_id=node_e.id, relation_type="parent"))
    
    # Query with type="related"
    graph_filtered = await service.get_knowledge_graph(node_a.id, depth=2, relation_type="related")
    
    node_ids_filtered = {node.id for node in graph_filtered["nodes"]}
    assert node_e.id not in node_ids_filtered
    assert node_c.id in node_ids_filtered
    
    # Query with type="parent"
    # Starting from A, there are no "parent" edges. So we should only get A.
    graph_parent = await service.get_knowledge_graph(node_a.id, depth=2, relation_type="parent")
    assert len(graph_parent["nodes"]) == 1
    assert graph_parent["nodes"][0].id == node_a.id
    assert len(graph_parent["edges"]) == 0
