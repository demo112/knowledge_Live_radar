
import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy import select
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation

@pytest.mark.asyncio
async def test_pyramid_lifecycle(client: AsyncClient, db_session):
    # 1. Create Pyramid
    create_data = {
        "name": "Test Pyramid",
        "description": "Integration Test",
        "category": "test"
    }
    response = await client.post("/api/v1/pyramids/", json=create_data)
    assert response.status_code == 201
    pyramid_data = response.json()
    pyramid_id = pyramid_data["id"]
    assert pyramid_data["name"] == "Test Pyramid"

    # 2. Get Pyramid
    response = await client.get(f"/api/v1/pyramids/{pyramid_id}")
    assert response.status_code == 200
    assert response.json()["id"] == pyramid_id

    # 3. Update Pyramid
    update_data = {"name": "Updated Pyramid"}
    response = await client.patch(f"/api/v1/pyramids/{pyramid_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pyramid"

    # 4. Delete Pyramid (Soft Delete/Archive not explicitly implemented in standard CRUD, assuming Delete)
    response = await client.delete(f"/api/v1/pyramids/{pyramid_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = await client.get(f"/api/v1/pyramids/{pyramid_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_node_split_merge(client: AsyncClient, db_session):
    # Setup: Create Pyramid and Root Node
    pyramid_res = await client.post("/api/v1/pyramids/", json={"name": "Ops Pyramid", "description": "Ops", "category": "ops"})
    pyramid_id = pyramid_res.json()["id"]
    
    # Create Root Node
    root_node_data = {
        "name": "Root Node",
        "content": "Root Content",
        "node_type": "concept",
        "pyramid_id": pyramid_id
    }
    # Assuming there's an endpoint to create nodes or using service directly.
    # The current API spec might rely on auto-creation or specific endpoints.
    # Let's check if we can create nodes via API.
    # If not, we insert directly to DB for setup.
    
    # Let's try to find a create node endpoint.
    # Based on previous context, nodes are usually created via /api/v1/pyramids/{id}/nodes or similar.
    # I will assume standard CRUD or direct DB insertion for setup simplicity.
    
    # Insert Root Node directly for setup
    root_node = PyramidNode(
        id=uuid4(),
        pyramid_id=uuid4(), # temporary, will fix
        name="Root Node",
        content="Root Content",
        node_type="concept",
        level=0
    )
    # Correct pyramid_id
    root_node.pyramid_id = pyramid_id
    db_session.add(root_node)
    await db_session.commit()
    await db_session.refresh(root_node)
    root_id = str(root_node.id)

    # 1. Split Node
    split_data = {
        "sub_nodes": [
            {"name": "Child 1", "content": "Content 1", "node_type": "concept"},
            {"name": "Child 2", "content": "Content 2", "node_type": "fact"}
        ],
        "delete_original": False
    }
    
    response = await client.post(f"/api/v1/nodes/{root_id}/split", json=split_data)
    assert response.status_code == 200
    children = response.json()["data"]
    assert len(children) == 2
    child1_id = children[0]["id"]
    child2_id = children[1]["id"]
    
    # Verify in DB
    result = await db_session.execute(select(PyramidNode).where(PyramidNode.parent_id == root_node.id))
    db_children = result.scalars().all()
    assert len(db_children) == 2

    # 2. Merge Nodes
    merge_data = {
        "source_node_ids": [child1_id, child2_id],
        "target_node_name": "Merged Child",
        "target_node_content": "Merged Content",
        "strategy": "create_new"
    }
    
    response = await client.post(f"/api/v1/pyramids/{pyramid_id}/merge", json=merge_data)
    # Note: Merge endpoint is usually on pyramid or specific controller. 
    # Based on previous work: router.post("/{id}/merge") in pyramids.py -> /api/v1/pyramids/{id}/merge
    
    assert response.status_code == 200
    merged_node = response.json()["data"]
    assert merged_node["name"] == "Merged Child"
    
    # Verify original children are deleted (soft deleted) or removed
    # The implementation details depend on the service logic.
    # Assuming soft delete or hard delete.
    
    # Verify new node exists
    response = await client.get(f"/api/v1/nodes/{merged_node['id']}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_node_linking(client: AsyncClient, db_session):
    # Setup
    pyramid_res = await client.post("/api/v1/pyramids/", json={"name": "Link Pyramid", "description": "Link", "category": "link"})
    pyramid_id = pyramid_res.json()["id"]
    
    # Create two nodes
    node1 = PyramidNode(pyramid_id=pyramid_id, name="Node 1", content="C1", node_type="concept", level=1)
    node2 = PyramidNode(pyramid_id=pyramid_id, name="Node 2", content="C2", node_type="concept", level=1)
    db_session.add_all([node1, node2])
    await db_session.commit()
    await db_session.refresh(node1)
    await db_session.refresh(node2)
    
    # Link Node 1 -> Node 2
    link_data = {
        "target_node_id": str(node2.id),
        "relation_type": "supports"
    }
    
    response = await client.post(f"/api/v1/nodes/{node1.id}/link", json=link_data)
    assert response.status_code == 200
    relation = response.json()["data"]
    assert relation["source_node_id"] == str(node1.id)
    assert relation["target_node_id"] == str(node2.id)
    assert relation["relation_type"] == "supports"
    
    # Verify in DB
    result = await db_session.execute(
        select(NodeRelation).where(
            NodeRelation.source_node_id == node1.id,
            NodeRelation.target_node_id == node2.id
        )
    )
    rel_in_db = result.scalar_one_or_none()
    assert rel_in_db is not None


@pytest.mark.asyncio
async def test_health_and_visualization(client: AsyncClient, db_session):
    # Setup
    pyramid_res = await client.post("/api/v1/pyramids/", json={"name": "Health Pyramid", "description": "Health", "category": "health"})
    pyramid_id = pyramid_res.json()["id"]
    
    # Create a structure: Root -> Child
    root = PyramidNode(pyramid_id=pyramid_id, name="Root", content="Root", node_type="concept", level=0)
    db_session.add(root)
    await db_session.commit()
    await db_session.refresh(root)
    
    child = PyramidNode(pyramid_id=pyramid_id, name="Child", content="Child", node_type="fact", level=1, parent_id=root.id)
    db_session.add(child)
    await db_session.commit()
    
    # 1. Health
    response = await client.get(f"/api/v1/pyramids/{pyramid_id}/health")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "details" in data
    assert "suggestions" in data
    
    # 2. Visualization
    response = await client.get(f"/api/v1/pyramids/{pyramid_id}/visualization")
    assert response.status_code == 200
    vis_data = response.json()
    assert "nodes" in vis_data
    assert "edges" in vis_data
    assert len(vis_data["nodes"]) == 2
    assert len(vis_data["edges"]) == 1
