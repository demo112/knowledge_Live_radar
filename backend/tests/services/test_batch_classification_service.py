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
        
        # Create service
        service = BatchClassificationService()
        
        # Mock DB items
        item1_id = uuid.uuid4()
        item2_id = uuid.uuid4()
        item1 = ContentItem(id=item1_id, title="Test 1", url="http://test1.com", content_text="Content 1", ai_processed=False)
        item2 = ContentItem(id=item2_id, title="Test 2", url="http://test2.com", content_text="Content 2", ai_processed=False)
        items = [item1, item2]
        
        # Mock AsyncSessionLocal
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Setup execute return values
        # First call: select unclassified items -> returns items
        # Subsequent calls: select item by id -> returns item (we simplify by returning item1 for any query)
        mock_result_items = MagicMock()
        mock_result_items.scalars.return_value.all.return_value = items
        
        mock_result_single = MagicMock()
        mock_result_single.scalar_one_or_none.return_value = item1 # Just return something valid
        
        # We need side_effect to return different results for different calls
        # But AsyncSession.execute is async, so return_value should be a result that can be awaited if mocked as coroutine
        # or just return value if using AsyncMock on execute
        
        # Since mock_db.execute is an AsyncMock, it returns a coroutine that resolves to the return_value.
        # We want that return_value to be mock_result.
        
        # To handle multiple calls returning different things, we use side_effect on the return_value?
        # No, side_effect on execute.
        
        async def execute_side_effect(stmt, *args, **kwargs):
            # Very naive check of the statement
            s = str(stmt)
            if "ai_processed" in s or "WHERE content_items.ai_processed = false" in s or "ai_processed = :ai_processed_1" in s:
                 return mock_result_items
            return mock_result_single

        # However, verifying SQL string representation is flaky. 
        # Let's just return mock_result_items for the first call and mock_result_single for others if we can count calls.
        # But execute is called concurrently in phase 3 potentially? No, phase 3 is sequential loop.
        
        # Simpler approach: 
        # Just mock _process_single_item_ai to avoid full DB/AI integration test complexity 
        # and test _process_single_item_ai separately?
        
        # Let's try to mock AsyncSessionLocal properly.
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__.return_value = mock_db
        mock_session_ctx.__aexit__.return_value = None
        
        # We need to manually manage the side effect because side_effect with AsyncMock is tricky if not set up right
        # Let's just set return_value to mock_result_items, and for the update phase we don't care much what execute returns
        # as long as scalar_one_or_none works.
        # But if we return items list for scalar_one_or_none call, it might fail.
        
        mock_result_items.scalar_one_or_none.return_value = item1
        mock_db.execute.return_value = mock_result_items
        
        with patch("app.services.batch_classification_service.AsyncSessionLocal", return_value=mock_session_ctx):
            # Run execution
            result = await service._execute_batch_classification(batch_size=2)
            
            # Assertions
            assert result["processed_count"] == 2
            assert result["success_count"] == 2
            assert mock_ai_service.chat_completion.call_count == 2
            
            # Check if commit was called (once in Phase 3)
            assert mock_db.commit.called

@pytest.mark.asyncio
async def test_process_single_item_ai():
    with patch("app.services.batch_classification_service.ai_service") as mock_ai_service:
        mock_ai_service.chat_completion = AsyncMock(return_value='{"tags": ["Tag1"], "concepts": ["Concept1"], "summary": "Summary1"}')
        
        service = BatchClassificationService()
        item_data = {"id": uuid.uuid4(), "title": "Title", "url": "URL", "content_text": "Text"}
        
        result = await service._process_single_item_ai(item_data)
        
        assert result["success"] is True
        assert result["tags"] == ["Tag1"]
        assert result["concepts"] == ["Concept1"]
        assert result["summary"] == "Summary1"
