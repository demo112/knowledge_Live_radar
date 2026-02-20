import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pyramid import Pyramid, PyramidNode
from app.models.ai_suggestion import AISuggestion
from app.services.suggestion_executor import SuggestionExecutor
from app.core.ai.processors.suggestion import SuggestionProcessor

# Mock AI response matching the structure expected by SuggestionProcessor
MOCK_AI_RESPONSE = {
    "analysis": {
        "depth_balance_score": 80,
        "coverage_score": 70,
        "activity_score": 90,
        "overall_health": 80,
        "summary": "Test Summary"
    },
    "suggestions": [
        {
            "action_type": "update_node",
            "target_id": "NODE_ID_1",  # Will be replaced with real UUID
            "target_name": "Undescribed Node",
            "reason": "Missing description",
            "params": {
                "description": "Generated description for node 1 based on content samples."
            },
            "confidence": 0.9,
            "priority": "high"
        },
        {
            "action_type": "split_node",
            "target_id": "NODE_ID_2",  # Will be replaced with real UUID
            "target_name": "Overloaded Node",
            "reason": "Too much content",
            "params": {
                "node_id": "NODE_ID_2", # Required by executor
                "suggested_children": [
                    {
                        "name": "Child A",
                        "description": "Description for Child A"
                    },
                    {
                        "name": "Child B",
                        "description": "Description for Child B"
                    }
                ]
            },
            "confidence": 0.85,
            "priority": "high"
        }
    ]
}

@pytest.mark.asyncio
async def test_pyramid_evolution_workflow_with_descriptions(db_session: AsyncSession):
    """
    Test the full workflow:
    1. Analyze Pyramid Health (Mock AI) -> Generate Suggestions with Descriptions
    2. Store Suggestions
    3. Execute Suggestions -> Update/Create Nodes with Descriptions
    """
    
    # 1. Setup Pyramid and Nodes
    pyramid = Pyramid(name="Evolution Test Pyramid", description="Test")
    db_session.add(pyramid)
    await db_session.commit()
    await db_session.refresh(pyramid)
    
    # Node 1: Missing description (to be updated)
    node1 = PyramidNode(
        pyramid_id=pyramid.id, 
        name="Undescribed Node", 
        description=None,
        level=1,
        sort_order=0,
        path="/1/"  # Mock path
    )
    db_session.add(node1)
    
    # Node 2: To be split
    node2 = PyramidNode(
        pyramid_id=pyramid.id, 
        name="Overloaded Node", 
        description="Original Description",
        level=1,
        sort_order=1,
        path="/2/"  # Mock path
    )
    db_session.add(node2)
    
    await db_session.commit()
    await db_session.refresh(node1)
    await db_session.refresh(node2)
    
    # 2. Mock AI Response with real UUIDs
    mock_response = MOCK_AI_RESPONSE.copy()
    mock_response["suggestions"][0]["target_id"] = str(node1.id)
    mock_response["suggestions"][0]["params"]["node_id"] = str(node1.id) # Ensure param matches
    
    mock_response["suggestions"][1]["target_id"] = str(node2.id)
    mock_response["suggestions"][1]["params"]["node_id"] = str(node2.id)
    
    # 3. Run Analysis (Mocking AI Client)
    processor = SuggestionProcessor()
    
    with patch("app.core.ai.client.ai_client.chat_completion", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = json.dumps(mock_response)
        
        result = await processor.analyze_pyramid_health(str(pyramid.id), db=db_session)
        
        assert "error" not in result
        assert len(result["suggestions"]) == 2
        suggestion_ids = result["suggestion_ids"]
        assert len(suggestion_ids) == 2

    # 4. Verify Suggestions Stored in DB
    stmt = select(AISuggestion).where(AISuggestion.pyramid_id == pyramid.id)
    suggestions = (await db_session.execute(stmt)).scalars().all()
    assert len(suggestions) == 2
    
    suggestion_map = {s.action_type: s for s in suggestions}
    
    # Verify update_node suggestion
    update_sugg = suggestion_map["update_node"]
    assert update_sugg.target_id == node1.id
    assert update_sugg.params["description"] == "Generated description for node 1 based on content samples."
    
    # Verify split_node suggestion
    split_sugg = suggestion_map["split_node"]
    assert split_sugg.target_id == node2.id
    children = split_sugg.params["suggested_children"]
    assert len(children) == 2
    assert children[0]["name"] == "Child A"
    assert children[0]["description"] == "Description for Child A"
    
    # 5. Execute Suggestions
    executor = SuggestionExecutor(db_session)
    
    # Approve first
    update_sugg.status = "approved"
    split_sugg.status = "approved"
    await db_session.commit()
    
    # Execute update_node
    await executor.execute(str(update_sugg.id), db_session)
    
    # Execute split_node
    await executor.execute(str(split_sugg.id), db_session)
    
    # 6. Verify Database Updates
    
    # Check Node 1 (Updated Description)
    await db_session.refresh(node1)
    assert node1.description == "Generated description for node 1 based on content samples."
    
    # Check Node 2 Children (Created with Descriptions)
    stmt = select(PyramidNode).where(PyramidNode.parent_id == node2.id)
    new_children = (await db_session.execute(stmt)).scalars().all()
    assert len(new_children) == 2
    
    child_map = {c.name: c for c in new_children}
    assert "Child A" in child_map
    assert child_map["Child A"].description == "Description for Child A"
    assert "Child B" in child_map
    assert child_map["Child B"].description == "Description for Child B"
