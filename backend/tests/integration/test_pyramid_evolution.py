
import pytest
import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pyramid import Pyramid, PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.ai_suggestion import AISuggestion
from app.services.suggestion_executor import SuggestionExecutor
from app.services.pyramid_service import PyramidService
from app.core.ai.processors.suggestion import SuggestionProcessor
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate

@pytest.mark.asyncio
async def test_node_content_sampling(db_session: AsyncSession):
    """Test that content samples are correctly retrieved for nodes"""
    # Setup
    db = db_session
    pyramid = Pyramid(name="Evolution Test", description="Test")
    db.add(pyramid)
    await db.commit()
    await db.refresh(pyramid)
    
    node = PyramidNode(pyramid_id=pyramid.id, name="AI Topics", path="/")
    db.add(node)
    await db.commit()
    await db.refresh(node)
    
    # Add some content
    contents = []
    base_time = datetime.now()
    for i in range(5):
        c = ContentItem(
            title=f"AI Content {i}",
            url=f"http://test.com/{i}",
            content_text=f"Content body {i}",
            is_deleted=False,
            created_at=base_time + timedelta(minutes=i) # Explicit time for ordering
        )
        db.add(c)
        contents.append(c)
    await db.commit()
    
    # Link content to node
    for c in contents:
        rel = ContentNodeRelation(node_id=node.id, content_id=c.id, source="manual")
        db.add(rel)
    await db.commit()
    
    # Test Sampling
    processor = SuggestionProcessor()
    samples = await processor._get_node_content_samples(pyramid.id, db, limit_per_node=3)
    
    assert str(node.id) in samples
    node_samples = samples[str(node.id)]
    assert len(node_samples) == 3
    # Should get the latest ones (4, 3, 2)
    assert "AI Content 4" in node_samples
    assert "AI Content 3" in node_samples
    assert "AI Content 2" in node_samples

@pytest.mark.asyncio
async def test_evolution_execution_split_node(db_session: AsyncSession):
    """
    Test split_node execution with descriptions (simulating AI output)
    """
    db = db_session
    pyramid = Pyramid(name="Evolution Execution", description="Test")
    db.add(pyramid)
    await db.commit()
    await db.refresh(pyramid)
    
    node = PyramidNode(pyramid_id=pyramid.id, name="Overloaded Node", path="/")
    db.add(node)
    await db.commit()
    await db.refresh(node)
    
    # Simulated Suggestion from AI
    params = {
        "node_id": str(node.id),
        "suggested_children": [
            {"name": "Machine Learning", "description": "Core ML algorithms and theory"},
            {"name": "Deep Learning", "description": "Neural networks and deep architectures"}
        ]
    }
    
    suggestion = AISuggestion(
        pyramid_id=pyramid.id,
        action_type="split_node",
        type="structural_optimization",
        data={},
        input_hash="evolution_test_hash",
        params=params,
        status="approved"
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Execute
    executor = SuggestionExecutor(db)
    result = await executor.execute(str(suggestion.id), db)
    
    assert result["success"] is True
    
    # Verify
    stmt = select(PyramidNode).where(PyramidNode.parent_id == node.id)
    children = (await db.execute(stmt)).scalars().all()
    
    assert len(children) == 2
    child_map = {c.name: c for c in children}
    
    assert "Machine Learning" in child_map
    assert child_map["Machine Learning"].description == "Core ML algorithms and theory"
    
    assert "Deep Learning" in child_map
    assert child_map["Deep Learning"].description == "Neural networks and deep architectures"

@pytest.mark.asyncio
async def test_evolution_execution_merge_node(db_session: AsyncSession):
    """Test merge_node execution, ensuring it works without pyramid_id in params"""
    # Setup
    db = db_session
    pyramid = Pyramid(name="Test Pyramid Merge", description="Test Description")
    db.add(pyramid)
    await db.commit()
    await db.refresh(pyramid)
    
    node1 = PyramidNode(pyramid_id=pyramid.id, name="Node 1", path="/", level=0)
    node2 = PyramidNode(pyramid_id=pyramid.id, name="Node 2", path="/", level=0)
    db.add(node1)
    db.add(node2)
    await db.commit()
    await db.refresh(node1)
    await db.refresh(node2)
    
    # Create Suggestion without pyramid_id in params
    params = {
        "source_node_ids": [str(node1.id), str(node2.id)],
        "target_node_name": "Merged Node",
        "target_node_description": "Merged Description"
    }
    suggestion = AISuggestion(
        pyramid_id=pyramid.id,
        action_type="merge_node",
        type="structural_optimization",
        data={},
        input_hash="test_hash_merge",
        params=params,
        status="approved"
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Execute
    executor = SuggestionExecutor(db)
    
    # This should SUCCEED (fixed bug)
    result = await executor.execute(str(suggestion.id), db)
    assert result["success"] is True
    assert result["data"]["action"] == "merge_node"
    
    # Verify merged node exists
    merged_node_id = result["data"]["merged_node_id"]
    stmt = select(PyramidNode).where(PyramidNode.id == uuid.UUID(merged_node_id))
    merged_node = (await db.execute(stmt)).scalar_one()
    assert merged_node.name == "Merged Node"
    assert merged_node.description == "Merged Description"

@pytest.mark.asyncio
async def test_evolution_execution_create_node(db_session: AsyncSession):
    """Test create_node execution"""
    # Setup
    db = db_session
    pyramid = Pyramid(name="Test Pyramid Create", description="Test Description")
    db.add(pyramid)
    await db.commit()
    await db.refresh(pyramid)
    
    # Create Suggestion
    params = {
        "name": "New Node",
        "description": "Generated by AI",
        "parent_id": None
    }
    suggestion = AISuggestion(
        pyramid_id=pyramid.id,
        action_type="create_node",
        type="structural_optimization",
        data={},
        input_hash="test_hash_create",
        params=params,
        status="approved"
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Execute
    executor = SuggestionExecutor(db)
    result = await executor.execute(str(suggestion.id), db)
    
    # Verify
    assert result["success"] is True
    assert result["data"]["action"] == "create_node"
    
    # Check Node in DB
    service = PyramidService(db)
    nodes = await service.get_nodes(pyramid.id)
    created_node = next((n for n in nodes if n.name == "New Node"), None)
    assert created_node is not None
    assert created_node.description == "Generated by AI"

@pytest.mark.asyncio
async def test_evolution_execution_move_node(db_session: AsyncSession):
    """Test move_node execution with recursive path updates"""
    # Setup
    db = db_session
    pyramid = Pyramid(name="Test Pyramid Move", description="Test Description")
    db.add(pyramid)
    await db.commit()
    await db.refresh(pyramid)
    
    # Create Structure: Root -> Parent -> Child -> Grandchild
    root = PyramidNode(pyramid_id=pyramid.id, name="Root", path="/", level=0)
    db.add(root)
    await db.commit()
    await db.refresh(root)
    
    parent = PyramidNode(pyramid_id=pyramid.id, name="Parent", parent_id=root.id, path=f"/{root.id}/", level=1)
    db.add(parent)
    await db.commit()
    await db.refresh(parent)
    
    child = PyramidNode(pyramid_id=pyramid.id, name="Child", parent_id=parent.id, path=f"/{root.id}/{parent.id}/", level=2)
    db.add(child)
    await db.commit()
    await db.refresh(child)

    grandchild = PyramidNode(pyramid_id=pyramid.id, name="Grandchild", parent_id=child.id, path=f"/{root.id}/{parent.id}/{child.id}/", level=3)
    db.add(grandchild)
    await db.commit()
    await db.refresh(grandchild)
    
    # New Parent (Sibling of Parent)
    new_parent = PyramidNode(pyramid_id=pyramid.id, name="New Parent", parent_id=root.id, path=f"/{root.id}/", level=1)
    db.add(new_parent)
    await db.commit()
    await db.refresh(new_parent)
    
    # Create Suggestion: Move Child to New Parent
    params = {
        "node_id": str(child.id),
        "target_parent_id": str(new_parent.id)
    }
    suggestion = AISuggestion(
        pyramid_id=pyramid.id,
        target_id=child.id,
        target_type="pyramid_node",
        action_type="move_node",
        type="structural_optimization",
        data={},
        input_hash="test_hash_move",
        params=params,
        status="approved"
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Execute
    executor = SuggestionExecutor(db)
    result = await executor.execute(str(suggestion.id), db)
    
    # Verify
    assert result["success"] is True
    
    # Check Paths
    await db.refresh(child)
    await db.refresh(grandchild)
    
    expected_child_path = f"/{root.id}/{new_parent.id}/"
    assert child.parent_id == new_parent.id
    assert child.path == expected_child_path
    
    # Verify recursive update
    expected_grandchild_path = f"/{root.id}/{new_parent.id}/{child.id}/"
    assert grandchild.path == expected_grandchild_path
