import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.evolution.health_detector import HealthDetector

@pytest.mark.asyncio
async def test_evaluate_source_health_empty():
    # Mock DB session
    mock_db = AsyncMock()
    
    # Mock result for sources query (empty list)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    detector = HealthDetector(mock_db)
    
    # Mock AI client to avoid real calls
    with patch("app.services.evolution.health_detector.ai_client") as mock_ai:
        # Mocking generate_issue_description behavior if needed, 
        # but since it calls prompt_loader and ai_client, we mock ai_client mostly.
        # Or better, mock _generate_issue_description directly to isolate the logic.
        
        with patch.object(detector, '_generate_issue_description', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "description": "System has no sources",
                "suggestions": [{"action": "add_source", "detail": "Add sources", "priority": "high"}],
                "impact": "Cannot fetch content"
            }
            
            score, issues = await detector.evaluate_source_health()
            
            assert score == 0.0
            assert len(issues) == 1
            assert issues[0]["type"] == "no_sources"
            assert issues[0]["severity"] == "high"
            assert issues[0]["description"] == "System has no sources"

@pytest.mark.asyncio
async def test_evaluate_pyramid_structure_empty():
    # Mock DB session
    mock_db = AsyncMock()
    
    # Mock result for pyramids query (empty list)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    detector = HealthDetector(mock_db)
    
    with patch.object(detector, '_generate_issue_description', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {
            "description": "System has no pyramids",
            "suggestions": [{"action": "create_pyramid", "detail": "Create one", "priority": "high"}],
            "impact": "No structure"
        }
        
        scores, issues = await detector.evaluate_pyramid_structure()
        
        assert scores == {}
        assert len(issues) == 1
        assert issues[0]["type"] == "no_pyramids"
        assert issues[0]["severity"] == "high"
