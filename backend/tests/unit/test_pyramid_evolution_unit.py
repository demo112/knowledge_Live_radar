
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.pyramid_service import PyramidService
from app.models.pyramid import Pyramid, PyramidNode
from app.models.ai_suggestion import AISuggestion
from app.schemas.pyramid import PyramidCreate

@pytest.mark.asyncio
async def test_analyze_structure(db_session: AsyncSession):
    # 1. Setup Pyramid
    service = PyramidService(db_session)
    pyramid_schema = PyramidCreate(name="Test Pyramid", description="Test Desc")
    pyramid = await service.create_pyramid(pyramid_schema)
    
    # 2. Mock AI Facade
    mock_suggestions = [
        {
            "action_type": "split_node",
            "target_id": str(uuid.uuid4()),
            "target_name": "Test Node",
            "confidence": 0.8,
            "reason": "Too complex",
            "params": {"suggested_children": ["Child A", "Child B"]}
        }
    ]
    
    with patch("app.core.ai.facade.ai_facade.analyze_pyramid_health", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {"suggestions": mock_suggestions}
        
        # 3. Call analyze_structure
        suggestions = await service.analyze_structure(pyramid.id)
        
        assert len(suggestions) == 1
        assert suggestions[0].action_type == "split_node"
        assert suggestions[0].status == "pending"
        
        # Verify saved to DB
        saved = await service.get_optimization_suggestions(pyramid.id)
        assert len(saved) == 1
        assert saved[0].id == suggestions[0].id

@pytest.mark.asyncio
async def test_detect_drift(db_session: AsyncSession):
    # 1. Setup Pyramid and Node
    service = PyramidService(db_session)
    pyramid_schema = PyramidCreate(name="Test Pyramid", description="Test Desc")
    pyramid = await service.create_pyramid(pyramid_schema)
    
    # Create a node manually or via service
    node = PyramidNode(
        pyramid_id=pyramid.id,
        name="Test Node",
        description="Desc",
        level=0,
        path="/"
    )
    db_session.add(node)
    await db_session.commit()
    await db_session.refresh(node)
    
    # 2. Mock AI Facade
    mock_suggestions = [
        {
            "action_type": "fix_drift",
            "target_id": str(node.id),
            "params": {"new_description": "Updated Desc"}
        }
    ]
    mock_result = {
        "analysis": {
            "drift_detected": True,
            "drift_score": 0.9,
            "drift_details": "Content changed significantly"
        },
        "suggestions": mock_suggestions
    }
    
    with patch("app.core.ai.facade.ai_facade.analyze_concept_drift", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_result
        
        # 3. Call detect_drift
        suggestions = await service.detect_drift(pyramid.id)
        
        assert len(suggestions) == 1
        assert suggestions[0].type == "concept_drift"
        assert suggestions[0].action_type == "fix_drift"
        assert suggestions[0].target_id == node.id
        
        # Verify saved to DB
        saved = await service.get_optimization_suggestions(pyramid.id)
        assert len(saved) == 1

@pytest.mark.asyncio
async def test_apply_suggestion(db_session: AsyncSession):
    # 1. Setup Pyramid
    service = PyramidService(db_session)
    pyramid_schema = PyramidCreate(name="Test Pyramid", description="Test Desc")
    pyramid = await service.create_pyramid(pyramid_schema)
    
    # 2. Create a pending suggestion
    suggestion = AISuggestion(
        type="structure_optimization",
        action_type="update_node", # Use a simple action that we can mock easily
        target_type="pyramid_node",
        pyramid_id=pyramid.id,
        status="pending",
        reason="Test reason",
        params={"node_id": str(uuid.uuid4())}, # Dummy ID, we will mock execution
        data={},
        input_hash="test_hash"
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)
    
    # 3. Mock SuggestionExecutor
    with patch("app.services.suggestion_executor.SuggestionExecutor.execute", new_callable=AsyncMock) as mock_execute:
        with patch("app.services.suggestion_executor.SuggestionExecutor.approve", new_callable=AsyncMock) as mock_approve:
            mock_approve.return_value = {"success": True}
            mock_execute.return_value = {"success": True, "data": {}}
            
            # 4. Call apply_suggestion
            result = await service.apply_suggestion(suggestion.id)
            
            assert result["success"] is True
            mock_approve.assert_called_once() # Should be called because it was pending
            mock_execute.assert_called_once()

