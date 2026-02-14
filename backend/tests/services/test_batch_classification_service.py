import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.batch_classification_service import BatchClassificationService
from app.models.content import ContentItem
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_batch_classification_service_execution():
    # Mock AI Service
    with patch("app.services.batch_classification_service.ai_service") as mock_ai_service:
        # Return valid JSON
        mock_ai_service.chat_completion = AsyncMock(return_value='{"tags": ["AI", "Python"], "concepts": ["Machine Learning"], "summary": "A summary"}')
        
        # Mock EvolutionEngine
        with patch("app.services.batch_classification_service.EvolutionEngine") as MockEvolutionEngine:
            mock_evolution_engine = MockEvolutionEngine.return_value
            mock_evolution_engine.auto_classify_content = AsyncMock(return_value=1)

            # Create service
            service = BatchClassificationService()
            
            # Mock DB items
            item1_id = uuid.uuid4()
            item2_id = uuid.uuid4()
            item1 = ContentItem(id=item1_id, title="Test 1", url="http://test1.com", content_text="Content 1", ai_processed=False)
            item2 = ContentItem(id=item2_id, title="Test 2", url="http://test2.com", content_text="Content 2", ai_processed=False)
            items = [item1, item2]
            
            # Mock AsyncSessionLocal
            # We need to mock the context manager: async with AsyncSessionLocal() as db:
            mock_db = AsyncMock(spec=AsyncSession)
            
            # Mock result object that supports both scalars().all() and scalar_one_or_none()
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = items
            mock_result.scalar_one_or_none.return_value = item1
            
            # Setup db.execute to return this mock_result
            mock_db.execute.return_value = mock_result
            
            # Setup AsyncSessionLocal to return the mock_db when used as context manager
            mock_session_ctx = MagicMock()
            mock_session_ctx.__aenter__.return_value = mock_db
            mock_session_ctx.__aexit__.return_value = None
            
            # Patch AsyncSessionLocal
            with patch("app.services.batch_classification_service.AsyncSessionLocal", return_value=mock_session_ctx):
                # Run execution
                result = await service._execute_batch_classification(batch_size=2)
                
                # Assertions
                assert result["processed_count"] == 2
                assert result["success_count"] == 2
                
                # Verify AI service was called twice
                assert mock_ai_service.chat_completion.call_count == 2
                
                # Verify EvolutionEngine was called twice
                assert mock_evolution_engine.auto_classify_content.call_count == 2
                
                # Verify commit was called (once per item in loop)
                assert mock_db.commit.call_count == 2

@pytest.mark.asyncio
async def test_process_single_item_ai():
    # Use patch context manager on the import path
    with patch("app.services.batch_classification_service.ai_service") as mock_ai_service:
        mock_ai_service.chat_completion = AsyncMock(return_value='{"tags": ["Tag1"], "concepts": ["Concept1"], "summary": "Summary1"}')
        
        service = BatchClassificationService()
        item_data = {"id": uuid.uuid4(), "title": "Title", "url": "URL", "content_text": "Text"}
        
        result = await service._process_single_item_ai(item_data)
        
        assert result["success"] is True
        assert result["tags"] == ["Tag1"]
        assert result["concepts"] == ["Concept1"]
        assert result["summary"] == "Summary1"
