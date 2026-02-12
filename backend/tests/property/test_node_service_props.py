import pytest
import pytest_asyncio
import uuid
from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, Bundle
from app.services.pyramid_service import PyramidService
from app.models.pyramid import Pyramid, PyramidNode
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate, PyramidNodeUpdate
from sqlalchemy import select
from fastapi import HTTPException

# 节点层级策略
@st.composite
def node_hierarchy_strategy(draw):
    levels = draw(st.integers(min_value=1, max_value=5))
    return levels

@pytest.mark.asyncio
async def test_property_6_node_update_consistency(db_session):
    """Property 6: 节点更新一致性 (Node Update Consistency)"""
    service = PyramidService(db_session)
    
    # Setup
    pyramid = await service.create_pyramid(PyramidCreate(name="Update Test"))
    node = await service.add_node(pyramid.id, PyramidNodeCreate(name="Original", description="Desc"))
    
    # Manual loop for async property testing
    for i in range(20):
        name = f"Updated Name {i} {uuid.uuid4()}"
        description = f"Updated Desc {i} {uuid.uuid4()}"
        
        # Update
        updated_node = await service.update_node(
            node.id, 
            PyramidNodeUpdate(name=name, description=description)
        )
        
        # Verify return value
        assert updated_node.name == name
        assert updated_node.description == description
        
        # Verify persistence
        fetched_node = await service.get_node(node.id)
        assert fetched_node.name == name
        assert fetched_node.description == description

@pytest.mark.asyncio
async def test_property_7_node_delete_cascade(db_session):
    """Property 7: 节点删除级联性 (Node Delete Cascade)"""
    service = PyramidService(db_session)
    
    # Setup Hierarchy: Root -> Child -> Grandchild
    pyramid = await service.create_pyramid(PyramidCreate(name="Cascade Test"))
    root = await service.add_node(pyramid.id, PyramidNodeCreate(name="Root"))
    child = await service.add_node(pyramid.id, PyramidNodeCreate(name="Child", parent_id=root.id))
    grandchild = await service.add_node(pyramid.id, PyramidNodeCreate(name="Grandchild", parent_id=child.id))
    
    # Delete Root
    await service.delete_node(root.id)
    
    # Verify Soft Deletion
    with pytest.raises(HTTPException) as excinfo:
        await service.get_node(root.id)
    assert excinfo.value.status_code == 404
        
    with pytest.raises(HTTPException) as excinfo:
        await service.get_node(child.id)
    assert excinfo.value.status_code == 404
        
    with pytest.raises(HTTPException) as excinfo:
        await service.get_node(grandchild.id)
    assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_property_8_node_move_subtree(db_session):
    """Property 8: 节点移动子树完整性 (Node Move Subtree Integrity)"""
    service = PyramidService(db_session)
    
    # Setup: Root1 -> Child1, Root2
    pyramid = await service.create_pyramid(PyramidCreate(name="Move Test"))
    root1 = await service.add_node(pyramid.id, PyramidNodeCreate(name="Root1"))
    child1 = await service.add_node(pyramid.id, PyramidNodeCreate(name="Child1", parent_id=root1.id))
    root2 = await service.add_node(pyramid.id, PyramidNodeCreate(name="Root2"))
    
    # Move Child1 to Root2
    await service.move_node(child1.id, new_parent_id=root2.id)
    
    # Verify
    moved_child = await service.get_node(child1.id)
    assert moved_child.parent_id == root2.id
    assert moved_child.path.startswith(root2.path) # Verify path update
    assert moved_child.level == root2.level + 1 # Verify level update

@pytest.mark.asyncio
async def test_property_15_recursive_query_integrity(db_session):
    """Property 15: 递归查询完整性 (Recursive Query Integrity)"""
    service = PyramidService(db_session)
    
    # Setup Deep Hierarchy
    pyramid = await service.create_pyramid(PyramidCreate(name="Recursive Test"))
    current_parent = None
    nodes = []
    for i in range(5):
        node = await service.add_node(pyramid.id, PyramidNodeCreate(name=f"Node {i}", parent_id=current_parent))
        nodes.append(node)
        current_parent = node.id
        
    # Verify Tree Structure Retrieval
    # Assuming get_pyramid_details returns nested nodes or we have a method to get descendants
    details = await service.get_pyramid_details(pyramid.id)
    
    # Simple check: all nodes present
    assert len(details.nodes) == 5
    
    # Check paths
    for i, node in enumerate(nodes):
        fetched = next(n for n in details.nodes if n.id == node.id)
        assert fetched.level == i
        if i > 0:
            assert str(nodes[i-1].id) in fetched.path
