import asyncio
import logging
from typing import Set, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.database import AsyncSessionLocal
from app.services.content_processor import content_processor
from app.services.source_lifecycle_manager import SourceLifecycleManager
from app.models.source import InformationSource
from sqlalchemy import select

logger = logging.getLogger(__name__)

class CrawlManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CrawlManager, cls).__new__(cls)
            cls._instance.queue = asyncio.PriorityQueue()
            cls._instance.active_jobs = set()  # Set[UUID]
            cls._instance.workers = []
            cls._instance.concurrency = 2
            cls._instance.is_running = False
        return cls._instance

    async def start(self):
        if not self.is_running:
            self.is_running = True
            self.workers = [
                asyncio.create_task(self._worker(i))
                for i in range(self.concurrency)
            ]
            logger.info(f"CrawlManager started with {self.concurrency} workers")

    async def stop(self):
        if self.is_running:
            self.is_running = False
            for worker in self.workers:
                worker.cancel()
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers = []
            logger.info("CrawlManager stopped")

    async def add_task(self, source_id: UUID, job_id: UUID = None, priority: int = 1):
        """
        Add a crawl task to the queue.
        Priority: 0 (High/Manual), 1 (Normal/Scheduled), 2 (Low/Retry)
        """
        if source_id in self.active_jobs:
            logger.info(f"Source {source_id} is already being crawled, skipping.")
            return

        # Check if already in queue (this is a simple check, ideally we'd peek)
        # For now, just add it. The worker checks active_jobs again.
        
        await self.queue.put((priority, source_id, job_id))
        logger.info(f"Added crawl task for source {source_id} with priority {priority}")

    async def _worker(self, worker_id: int):
        logger.debug(f"Worker {worker_id} started")
        while self.is_running:
            try:
                priority, source_id, job_id = await self.queue.get()
                
                if source_id in self.active_jobs:
                    self.queue.task_done()
                    continue

                self.active_jobs.add(source_id)
                
                try:
                    logger.info(f"Worker {worker_id} processing source {source_id}")
                    async with AsyncSessionLocal() as session:
                        source = await session.get(InformationSource, source_id)
                        if not source:
                            logger.warning(f"Source {source_id} not found")
                            continue
                        
                        job = None
                        if job_id:
                            from app.models.crawl_job import CrawlJob
                            job = await session.get(CrawlJob, job_id)
                            
                        job = await content_processor.process_source(source, session, job=job)
                        
                        # Lifecycle management is handled inside content_processor
                        
                except Exception as e:
                    logger.error(f"Worker {worker_id} error processing source {source_id}: {e}")
                finally:
                    self.active_jobs.remove(source_id)
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} loop error: {e}")
                await asyncio.sleep(1) # Prevent tight loop on error

crawl_manager = CrawlManager()
