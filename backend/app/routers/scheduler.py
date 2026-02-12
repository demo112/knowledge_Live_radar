from typing import List, Optional, Any, Dict
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.scheduled_task import ScheduledTask
from app.models.task_execution import TaskExecution
from app.services.scheduler.scheduler_service import SchedulerService

# Assuming Pydantic models for response
from pydantic import BaseModel
from datetime import datetime

class ScheduledTaskRead(BaseModel):
    id: uuid.UUID
    task_name: str
    task_type: str
    cron_expression: str
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskExecutionRead(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/scheduler",
    tags=["scheduler"]
)

@router.get("/tasks", response_model=List[ScheduledTaskRead])
async def list_tasks(
    db: AsyncSession = Depends(get_db)
):
    """
    List all scheduled tasks.
    """
    result = await db.execute(select(ScheduledTask).order_by(ScheduledTask.task_name))
    return result.scalars().all()

@router.get("/tasks/{task_id}", response_model=ScheduledTaskRead)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get task details.
    """
    result = await db.execute(select(ScheduledTask).where(ScheduledTask.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/trigger")
async def trigger_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger a task execution.
    """
    scheduler = SchedulerService()
    success = await scheduler.trigger_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to trigger task")
    return {"status": "triggered", "message": "Task triggered successfully"}

@router.put("/tasks/{task_id}/pause")
async def pause_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Pause a scheduled task.
    """
    scheduler = SchedulerService()
    success = await scheduler.pause_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause task")
    return {"status": "paused", "message": "Task paused"}

@router.put("/tasks/{task_id}/resume")
async def resume_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Resume a paused task.
    """
    scheduler = SchedulerService()
    success = await scheduler.resume_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resume task")
    return {"status": "resumed", "message": "Task resumed"}

@router.get("/executions", response_model=List[TaskExecutionRead])
async def list_executions(
    task_id: Optional[uuid.UUID] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List task execution history.
    """
    query = select(TaskExecution).order_by(desc(TaskExecution.started_at)).offset(offset).limit(limit)
    
    if task_id:
        query = query.where(TaskExecution.task_id == task_id)
        
    result = await db.execute(query)
    return result.scalars().all()
