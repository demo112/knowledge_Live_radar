
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pyramid import Pyramid, PyramidNode
from app.models.ai_suggestion import AISuggestion
from app.services.suggestion_executor import SuggestionExecutor

@pytest.mark.asyncio
async def test_merge_node_missing_pyramid_id_in_params(db_session: AsyncSession):
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
    
    # This should SUCCEED now
    result = await executor.execute(str(suggestion.id), db)
    assert result["success"] is True
    assert result["data"]["action"] == "merge_node"
