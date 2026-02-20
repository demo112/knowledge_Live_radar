
import pytest
import uuid
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pyramid import Pyramid, PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.ai_suggestion import AISuggestion
from app.services.suggestion_executor import suggestion_executor
from app.core.ai.processors.suggestion import SuggestionProcessor
from app.schemas.pyramid import PyramidNodeCreate

from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_node_content_sampling(db_session: AsyncSession):
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
    base_time = datetime.utcnow()
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
    assert "AI Content 4" in node_samples # Latest first
    assert "AI Content 3" in node_samples
    assert "AI Content 2" in node_samples

@pytest.mark.asyncio
async def test_evolution_execution_flow(db_session: AsyncSession):
    """
    Simulate the flow:
    1. Analysis suggests split with descriptions (Simulated)
    2. Execution applies split
    3. Verify descriptions
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
    
    # Simulated Suggestion from AI (Analysis Step skipped, assuming it worked)
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
    
    # Execute
    executor = suggestion_executor(db)
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
