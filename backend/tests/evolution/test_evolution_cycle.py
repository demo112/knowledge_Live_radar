import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.evolution.evolution_engine import evolution_engine
from app.models.health_report import HealthReport
from app.models.pyramid import Pyramid
from app.models.source import InformationSource

@pytest.mark.asyncio
async def test_evolution_cycle_execution(db_session: AsyncSession):
    """
    Test that the evolution cycle runs without errors and produces a health report.
    """
    # 1. Setup Data
    # Create a dummy source
    source = InformationSource(
        name="Test Source",
        url="http://example.com",
        type="RSS",
        status="DISCOVERED"
    )
    db_session.add(source)
    
    # Create a dummy pyramid
    pyramid = Pyramid(
        name="Test Pyramid",
        description="Test Description"
    )
    db_session.add(pyramid)
    
    await db_session.commit()
    
    # Mock AsyncSessionLocal to return our db_session
    # EvolutionEngine does: async with AsyncSessionLocal() as db:
    mock_session_factory = MagicMock()
    # The factory is called: AsyncSessionLocal() -> returns context manager
    # Context manager __aenter__ -> returns session
    mock_session_factory.return_value.__aenter__.return_value = db_session
    mock_session_factory.return_value.__aexit__.return_value = None
    
    # Patch where it is IMPORTED
    with patch("app.services.evolution.evolution_engine.AsyncSessionLocal", mock_session_factory):
        try:
            results = await evolution_engine.run_cycle()
            
            assert results is not None
            assert "health_score" in results
            assert results["strategies_updated"] >= 1
            assert results["hotspots_updated"] is True
            
            # 3. Verify Health Report Created
            report_result = await db_session.execute(select(HealthReport))
            reports = report_result.scalars().all()
            assert len(reports) >= 1
            latest_report = reports[-1]
            assert latest_report.overall_score >= 0
            
        except Exception as e:
            pytest.fail(f"Evolution cycle failed: {e}")
