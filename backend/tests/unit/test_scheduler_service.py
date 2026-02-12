import pytest
import uuid
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.scheduler.scheduler_service import SchedulerService
from app.models.scheduled_task import ScheduledTask
from app.models.task_execution import TaskExecution

@pytest.fixture
def scheduler_service():
    SchedulerService._instance = None
    service = SchedulerService()
    service.scheduler = MagicMock()
    return service

@pytest.mark.asyncio
async def test_execution_history_integrity(scheduler_service):
    """Property 16: Task execution history integrity"""
    with patch("app.services.scheduler.scheduler_service.AsyncSessionLocal") as mock_db:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        # Mock add to set ID
        def side_effect_add(obj):
            if isinstance(obj, TaskExecution):
                obj.id = uuid.uuid4()
        mock_session.add.side_effect = side_effect_add
        mock_db.return_value.__aenter__.return_value = mock_session
        
        task_id = uuid.uuid4()
        task = ScheduledTask(id=task_id, task_name="test", task_type="test", is_running=False, is_active=True)
        
        # Mock get calls:
        # 1. Get task (lock check)
        # 2. Get task (lock update) - wait, code uses same session or different?
        # Code uses AsyncSessionLocal() multiple times.
        # So we need mock_db to return a new session or same session each time.
        # AsyncSessionLocal() returns a mock whose __aenter__ returns mock_session.
        # So every `async with AsyncSessionLocal()` gets `mock_session`.
        
        # get(ScheduledTask, task_id) -> task
        # get(TaskExecution, execution_id) -> execution (mock)
        
        execution = TaskExecution(id=uuid.uuid4(), status="running")
        
        async def mock_get(model, id):
            if model == ScheduledTask:
                return task
            if model == TaskExecution:
                return execution
            return None
            
        mock_session.get.side_effect = mock_get
        
        with patch("app.services.scheduler.scheduler_service.TaskRegistry.get_handler", return_value=AsyncMock(return_value={"ok": True})):
            await scheduler_service._execute_wrapper(task_id, "test")
        
        # Check history recorded
        assert mock_session.add.called
        assert execution.status == "success"
        assert execution.result == {"ok": True}

@pytest.mark.asyncio
async def test_concurrency_protection(scheduler_service):
    """Property 19: Task concurrency protection"""
    with patch("app.services.scheduler.scheduler_service.AsyncSessionLocal") as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        task_id = uuid.uuid4()
        # Task is already running
        task = ScheduledTask(id=task_id, task_name="test", task_type="test", is_running=True, is_active=True)
        
        mock_session.get.return_value = task
        
        mock_task_handler = AsyncMock()
        with patch("app.services.scheduler.scheduler_service.TaskRegistry.get_handler", return_value=mock_task_handler) as mock_get_handler:
            await scheduler_service._execute_wrapper(task_id, "test")
            
            # Should NOT call handler
            mock_task_handler.assert_not_called()

@pytest.mark.asyncio
async def test_pause_resume_consistency(scheduler_service):
    """Property 18: Task pause/resume consistency"""
    with patch("app.services.scheduler.scheduler_service.AsyncSessionLocal") as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        task_id = uuid.uuid4()
        task = ScheduledTask(id=task_id, task_name="test", task_type="test", is_active=True, cron_expression="* * * * *")
        mock_session.get.return_value = task
        
        # Pause
        await scheduler_service.pause_task(task_id)
        assert task.is_active == False
        scheduler_service.scheduler.remove_job.assert_called_with(str(task_id))
        
        # Resume
        await scheduler_service.resume_task(task_id)
        assert task.is_active == True
        scheduler_service.scheduler.add_job.assert_called()
