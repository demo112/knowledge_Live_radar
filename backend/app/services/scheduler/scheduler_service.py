import uuid
import logging
import asyncio
import traceback
from datetime import datetime, timezone, timedelta
from typing import Optional, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.scheduled_task import ScheduledTask
from app.models.task_execution import TaskExecution
from app.services.scheduler.task_registry import TaskRegistry

logger = logging.getLogger(__name__)

class SchedulerService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            cls._instance.scheduler = AsyncIOScheduler()
            cls._instance.is_running = False
        return cls._instance

    async def start(self):
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started")
            await self._load_tasks()

    async def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")

    async def _load_tasks(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ScheduledTask))
            tasks = result.scalars().all()
            for task in tasks:
                if task.is_active:
                    self._schedule_job(task)

    def _schedule_job(self, task: ScheduledTask):
        try:
            trigger = CronTrigger.from_crontab(task.cron_expression)
            self.scheduler.add_job(
                self._execute_wrapper,
                trigger,
                id=str(task.id),
                name=task.task_name,
                args=[task.id, task.task_type],
                replace_existing=True
            )
            logger.info(f"Scheduled task {task.task_name} ({task.id})")
        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_name}: {e}")

    async def register_task(self, task_name: str, task_type: str, cron_expression: str) -> ScheduledTask:
        async with AsyncSessionLocal() as session:
            # Check if exists
            result = await session.execute(select(ScheduledTask).where(ScheduledTask.task_name == task_name))
            existing = result.scalars().first()
            
            if existing:
                if existing.cron_expression != cron_expression:
                    existing.cron_expression = cron_expression
                    await session.commit()
                    await session.refresh(existing)
                    if existing.is_active and self.is_running:
                        self._schedule_job(existing)
                return existing
            
            new_task = ScheduledTask(
                task_name=task_name,
                task_type=task_type,
                cron_expression=cron_expression,
                is_active=True
            )
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)
            
            if self.is_running:
                self._schedule_job(new_task)
            
            return new_task

    async def trigger_task(self, task_id: uuid.UUID) -> bool:
        # Trigger manually
        job = self.scheduler.get_job(str(task_id))
        if job:
            job.modify(next_run_time=datetime.now(timezone.utc))
            return True
        else:
            # If not in scheduler (e.g. inactive), load from DB and run once
            async with AsyncSessionLocal() as session:
                task = await session.get(ScheduledTask, task_id)
                if task:
                    await self._execute_wrapper(task.id, task.task_type)
                    return True
                return False

    async def pause_task(self, task_id: uuid.UUID) -> bool:
        async with AsyncSessionLocal() as session:
            task = await session.get(ScheduledTask, task_id)
            if task:
                task.is_active = False
                await session.commit()
                try:
                    self.scheduler.remove_job(str(task_id))
                except Exception:
                    pass # Job might not be in scheduler if it was already inactive/removed
                return True
            return False

    async def resume_task(self, task_id: uuid.UUID) -> bool:
        async with AsyncSessionLocal() as session:
            task = await session.get(ScheduledTask, task_id)
            if task:
                task.is_active = True
                await session.commit()
                self._schedule_job(task)
                return True
            return False

    async def _execute_wrapper(self, task_id, task_type):
        handler = TaskRegistry.get_handler(task_type)
        if not handler:
            logger.error(f"No handler found for task type: {task_type}")
            return

        async with AsyncSessionLocal() as session:
            task = await session.get(ScheduledTask, task_id)
            if not task:
                return
            
            if task.is_running:
                logger.warning(f"Task {task.task_name} skipped because it is already running")
                return
            
            task.is_running = True
            task.last_run_at = datetime.now(timezone.utc)
            await session.commit()

        # Create execution record
        execution = TaskExecution(
            task_id=task_id,
            status="running",
            started_at=datetime.now(timezone.utc)
        )
        
        async with AsyncSessionLocal() as session:
            session.add(execution)
            await session.commit()
            await session.refresh(execution)
            execution_id = execution.id

        try:
            # Execute handler
            start_time = datetime.now(timezone.utc)
            result = await handler()
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Update execution success
            async with AsyncSessionLocal() as session:
                execution = await session.get(TaskExecution, execution_id)
                execution.status = "success"
                execution.ended_at = end_time
                execution.duration_seconds = duration
                execution.result = result if isinstance(result, dict) else {"data": str(result)}
                await session.commit()
                
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds() if 'start_time' in locals() else 0
            logger.error(f"Task execution failed: {e}\n{traceback.format_exc()}")
            
            # Update execution failure
            async with AsyncSessionLocal() as session:
                execution = await session.get(TaskExecution, execution_id)
                execution.status = "failed"
                execution.ended_at = end_time
                execution.duration_seconds = duration
                execution.error_message = str(e)
                await session.commit()
                
            # TODO: Implement retry logic (ScheduledTask.max_retries)
            # For now, simple fail.
            
        finally:
            # Unlock task
            async with AsyncSessionLocal() as session:
                task = await session.get(ScheduledTask, task_id)
                if task:
                    task.is_running = False
                    await session.commit()

# Singleton
scheduler_service = SchedulerService()
