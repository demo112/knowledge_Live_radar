import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.services.batch_processor import BatchProcessor
from app.models.batch_task import BatchTask, BatchTaskStatus

@pytest.mark.asyncio
async def test_create_task():
    db = AsyncMock()
    # Ensure db.add is synchronous as in SQLAlchemy AsyncSession
    db.add = MagicMock()
    
    # Mock InputProcessor dependency if needed, but BatchProcessor.__init__ creates it.
    # Since InputProcessor takes db, it's fine.
    
    processor = BatchProcessor(db)
    
    task = await processor.create_task("url_import", 10, "user1")
    
    assert task.task_type == "url_import"
    assert task.total_items == 10
    assert task.user_id == "user1"
    assert task.status == BatchTaskStatus.PENDING
    
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
