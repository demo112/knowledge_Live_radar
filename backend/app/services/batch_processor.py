import logging
import uuid
import os
import aiofiles
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.batch_task import BatchTask, BatchTaskStatus
from app.services.input_processor import InputProcessor
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class LocalUploadFile:
    """Helper to mimic UploadFile for local files"""
    def __init__(self, path: str):
        self.path = path
        self.filename = os.path.basename(path)
        self.content_type = "application/octet-stream" # Generic
        self._file = None

    async def open(self):
        self._file = await aiofiles.open(self.path, 'rb')

    async def read(self, size: int = -1):
        if not self._file:
            await self.open()
        return await self._file.read(size)
        
    async def seek(self, offset: int):
        if not self._file:
            await self.open()
        await self._file.seek(offset)
        
    async def close(self):
        if self._file:
            await self._file.close()

class BatchProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.input_processor = InputProcessor(db)

    async def create_task(self, task_type: str, total_items: int, user_id: Optional[str] = None) -> BatchTask:
        task = BatchTask(
            id=uuid.uuid4(),
            task_type=task_type,
            total_items=total_items,
            user_id=user_id,
            status=BatchTaskStatus.PENDING,
            processed_items=0,
            failed_items=0
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: uuid.UUID) -> Optional[BatchTask]:
        result = await self.db.execute(select(BatchTask).where(BatchTask.id == task_id))
        return result.scalars().first()

    @staticmethod
    async def process_urls_background(task_id: uuid.UUID, urls: List[str], user_id: Optional[str] = None):
        """
        Background task to process a list of URLs.
        Creates its own database session.
        """
        async with AsyncSessionLocal() as db:
            try:
                processor = InputProcessor(db)
                task_result = await db.execute(select(BatchTask).where(BatchTask.id == task_id))
                task = task_result.scalars().first()
                
                if not task:
                    logger.error(f"Task {task_id} not found for background processing")
                    return

                task.status = BatchTaskStatus.PROCESSING
                await db.commit()
                
                processed_count = 0
                failed_count = 0
                results = []
                
                for url in urls:
                    try:
                        content_item = await processor.process_url_input(url, submitter_id=user_id)
                        results.append({"url": url, "status": "success", "id": str(content_item.id)})
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to process URL {url}: {e}")
                        failed_count += 1
                        results.append({"url": url, "status": "failed", "error": str(e)})
                
                task.processed_items = processed_count
                task.failed_items = failed_count
                task.result = {"details": results}
                
                if failed_count == 0:
                    task.status = BatchTaskStatus.COMPLETED
                elif processed_count > 0:
                    task.status = BatchTaskStatus.PARTIAL_SUCCESS
                else:
                    task.status = BatchTaskStatus.FAILED
                    task.error_message = "All items failed"
                    
                await db.commit()
                
            except Exception as e:
                logger.error(f"Critical error in batch task {task_id}: {e}")
                try:
                    if 'task' in locals() and task:
                        task.status = BatchTaskStatus.FAILED
                        task.error_message = f"Critical error: {str(e)}"
                        await db.commit()
                except Exception as inner_e:
                    logger.error(f"Failed to update task status: {inner_e}")

    @staticmethod
    async def process_files_background(task_id: uuid.UUID, file_paths: List[str], user_id: Optional[str] = None):
        """
        Background task to process a list of files.
        """
        async with AsyncSessionLocal() as db:
            try:
                processor = InputProcessor(db)
                task_result = await db.execute(select(BatchTask).where(BatchTask.id == task_id))
                task = task_result.scalars().first()
                
                if not task:
                    logger.error(f"Task {task_id} not found for background processing")
                    # Clean up temp files
                    for path in file_paths:
                        try:
                            os.remove(path)
                        except:
                            pass
                    return

                task.status = BatchTaskStatus.PROCESSING
                await db.commit()
                
                processed_count = 0
                failed_count = 0
                results = []
                
                for path in file_paths:
                    local_file = LocalUploadFile(path)
                    try:
                        # process_file_input expects UploadFile-like object
                        content_item = await processor.process_file_input(local_file, submitter_id=user_id)
                        results.append({"file": local_file.filename, "status": "success", "id": str(content_item.id)})
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to process file {path}: {e}")
                        failed_count += 1
                        results.append({"file": local_file.filename, "status": "failed", "error": str(e)})
                    finally:
                        await local_file.close()
                        # Remove temp file
                        try:
                            os.remove(path)
                        except Exception as e:
                            logger.warning(f"Failed to remove temp file {path}: {e}")
                
                task.processed_items = processed_count
                task.failed_items = failed_count
                task.result = {"details": results}
                
                if failed_count == 0:
                    task.status = BatchTaskStatus.COMPLETED
                elif processed_count > 0:
                    task.status = BatchTaskStatus.PARTIAL_SUCCESS
                else:
                    task.status = BatchTaskStatus.FAILED
                    task.error_message = "All items failed"
                    
                await db.commit()
                
            except Exception as e:
                logger.error(f"Critical error in batch task {task_id}: {e}")
                try:
                    if 'task' in locals() and task:
                        task.status = BatchTaskStatus.FAILED
                        task.error_message = f"Critical error: {str(e)}"
                        await db.commit()
                except Exception as inner_e:
                    logger.error(f"Failed to update task status: {inner_e}")
                
                # Ensure cleanup on critical error
                for path in file_paths:
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except:
                        pass
