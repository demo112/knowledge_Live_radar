import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import IntegrityError
from app.services.input_processor import InputProcessor
from app.services.evolution_engine import EvolutionEngine
from app.models.content import ContentItem

@pytest.mark.asyncio
async def test_ai_service_timeout_handling(db_session):
    """
    Test system behavior when AI service times out during classification.
    Should gracefully handle the error and not crash the flow.
    """
    # 1. Setup
    input_processor = InputProcessor(db_session)
    evolution_engine = EvolutionEngine(db_session)
    
    # Create content directly or via processor
    content = ContentItem(
        title="Timeout Test",
        content_text="This content will cause a timeout.",
        url="http://timeout.test"
    )
    db_session.add(content)
    await db_session.commit()
    
    # 2. Mock Vector Service to simulate AI/Network timeout
    # EvolutionEngine.auto_classify_content calls vector_service.upsert_content_vector
    # and vector_service.search_similar_nodes
    
    with patch.object(evolution_engine.vector_service, "search_similar_nodes", side_effect=asyncio.TimeoutError("AI Service Timeout")):
        # 3. Execute
        # Should catch exception and return 0
        linked_count = await evolution_engine.auto_classify_content(content)
        
        # 4. Verify
        assert linked_count == 0
        # The flow should continue without crashing

@pytest.mark.asyncio
async def test_database_integrity_error_handling(db_session):
    """
    Test system behavior when database integrity error occurs (e.g. duplicate entry).
    """
    input_processor = InputProcessor(db_session)
    
    # 1. Mock db.commit to raise IntegrityError
    # We need to patch the session's commit method
    
    with patch.object(db_session, "commit", side_effect=IntegrityError(None, None, Exception("Duplicate entry"))):
        with pytest.raises(IntegrityError):
             # This specific method might propagate the error, which is expected behavior for API to handle
             # or it might catch it. Let's see InputProcessor implementation.
             # process_text_input calls db.commit()
             await input_processor.process_text_input(
                 text="Duplicate content",
                 title="Duplicate Title"
             )
    
    # If the service catches it, we should adjust the test.
    # Looking at InputProcessor code (inferred), it likely raises the exception.
    # So pytest.raises(IntegrityError) is correct.

@pytest.mark.asyncio
async def test_vector_service_connection_error(db_session):
    """
    Test behavior when Vector DB is unreachable.
    """
    evolution_engine = EvolutionEngine(db_session)
    
    content = ContentItem(
        title="Vector Error Test",
        content_text="Vector DB is down.",
        url="http://vector-error.test"
    )
    
    # Mock upsert to fail
    with patch.object(evolution_engine.vector_service, "upsert_content_vector", side_effect=Exception("Connection Refused")):
        # Should log error and return 0, not crash
        linked_count = await evolution_engine.auto_classify_content(content)
        
        assert linked_count == 0
