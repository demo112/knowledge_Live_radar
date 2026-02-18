import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from app.services.evolution.evolution_engine import EvolutionEngine
from app.models.pyramid import Pyramid
from app.models.health_report import HealthReport

@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    # Mock context manager behavior
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    return session

@pytest.fixture
def mock_async_session_local(mock_db_session):
    with patch("app.services.evolution.evolution_engine.AsyncSessionLocal") as mock:
        mock.return_value = mock_db_session
        yield mock

@pytest.fixture
def mock_health_detector():
    with patch("app.services.evolution.evolution_engine.HealthDetector") as mock:
        instance = mock.return_value
        instance.run_full_detection = AsyncMock(return_value=HealthReport(overall_score=85.0))
        yield mock

@pytest.fixture
def mock_strategy_adapter():
    with patch("app.services.evolution.evolution_engine.StrategyAdapter") as mock:
        instance = mock.return_value
        instance.optimize_strategies = AsyncMock()
        yield mock

@pytest.fixture
def mock_hotspot_manager():
    with patch("app.services.evolution.evolution_engine.HotspotManager") as mock:
        instance = mock.return_value
        instance.update_hotspot_stats = AsyncMock()
        yield mock

@pytest.fixture
def mock_pyramid_service():
    with patch("app.services.evolution.evolution_engine.PyramidService") as mock:
        instance = mock.return_value
        instance.analyze_structure = AsyncMock(return_value=[1, 2]) # Returns 2 proposals
        instance.detect_drift = AsyncMock(return_value=[1]) # Returns 1 proposal
        yield mock

@pytest.mark.asyncio
async def test_run_cycle(
    mock_async_session_local,
    mock_db_session,
    mock_health_detector,
    mock_strategy_adapter,
    mock_hotspot_manager,
    mock_pyramid_service
):
    # Setup mock data
    pyramid1 = Pyramid(id=uuid4(), name="P1")
    pyramid2 = Pyramid(id=uuid4(), name="P2")
    
    # Mock DB execute result for pyramids
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [pyramid1, pyramid2]
    mock_db_session.execute.return_value = mock_result
    
    # Run engine
    engine = EvolutionEngine()
    results = await engine.run_cycle()
    
    # Verify results
    assert results["health_score"] == 85.0
    assert results["strategies_updated"] == 1
    assert results["hotspots_updated"] is True
    # 2 pyramids * 2 structure proposals = 4
    assert results["structure_proposals"] == 4 
    # 2 pyramids * 1 drift proposal = 2
    assert results["drift_proposals"] == 2
    assert len(results["errors"]) == 0
    
    # Verify interactions
    mock_health_detector.assert_called_once_with(mock_db_session)
    mock_strategy_adapter.assert_called_once_with(mock_db_session)
    mock_hotspot_manager.assert_called_once_with(mock_db_session)
    mock_pyramid_service.assert_called_once_with(mock_db_session)
    
    assert mock_pyramid_service.return_value.analyze_structure.call_count == 2
    assert mock_pyramid_service.return_value.detect_drift.call_count == 2
    
    mock_db_session.commit.assert_called_once()
