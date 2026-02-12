import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock
from app.services.batch_processor import BatchProcessor
from app.models.batch_task import BatchTaskStatus

# Helper to run async test with hypothesis
def async_test(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@given(
    task_type=st.text(min_size=1, max_size=50),
    total_items=st.integers(min_value=1, max_value=10000),
    user_id=st.one_of(st.none(), st.text(min_size=1, max_size=50))
)
@settings(max_examples=50)
def test_create_task_properties(task_type, total_items, user_id):
    async def run_test():
        db = AsyncMock()
        processor = BatchProcessor(db)
        
        task = await processor.create_task(task_type, total_items, user_id)
        
        assert task.task_type == task_type
        assert task.total_items == total_items
        assert task.user_id == user_id
        assert task.status == BatchTaskStatus.PENDING
        assert task.processed_items == 0
        assert task.failed_items == 0
        
        # Verify DB interactions
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    async_test(run_test())
