import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock
from app.services.input_processor import InputProcessor

# Helper to run async test
def async_test(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@given(
    text=st.text(min_size=1),
    title=st.text(min_size=1, max_size=100),
    submitter_id=st.one_of(st.none(), st.text(min_size=1, max_size=50))
)
@settings(max_examples=50)
def test_process_text_input_properties(text, title, submitter_id):
    async def run_test():
        db = AsyncMock()
        db.add = MagicMock()
        processor = InputProcessor(db)
        
        # Mock commit/refresh to avoid DB errors
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        item = await processor.process_text_input(text, title, submitter_id)
        
        assert item.content_text == text
        assert item.title == title
        assert item.submitter_id == submitter_id
        assert item.input_type == "text"
        assert item.status == "PENDING"
        
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        
    async_test(run_test())
