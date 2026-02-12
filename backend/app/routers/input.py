from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, ConfigDict
import uuid
import shutil
import tempfile
import os

from app.database import get_db
from app.services.input_processor import InputProcessor
from app.services.batch_processor import BatchProcessor
from app.models.content import ContentItem
from app.models.batch_task import BatchTask, BatchTaskStatus

router = APIRouter(prefix="/input", tags=["input"])

class UrlInput(BaseModel):
    url: HttpUrl
    
class TextInput(BaseModel):
    title: str
    content: str
    
class BatchUrlInput(BaseModel):
    urls: List[HttpUrl]

@router.post("/url", response_model=dict)
async def submit_url(input_data: UrlInput, db: AsyncSession = Depends(get_db)):
    """Submit a single URL for processing"""
    processor = InputProcessor(db)
    try:
        item = await processor.process_url_input(str(input_data.url))
        return {"success": True, "data": {"id": str(item.id), "title": item.title}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/file", response_model=dict)
async def submit_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Submit a file for processing (PDF, Word, MD, Text, Image)"""
    processor = InputProcessor(db)
    try:
        item = await processor.process_file_input(file)
        return {"success": True, "data": {"id": str(item.id), "title": item.title}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/text", response_model=dict)
async def submit_text(input_data: TextInput, db: AsyncSession = Depends(get_db)):
    """Submit raw text content"""
    processor = InputProcessor(db)
    try:
        item = await processor.process_text_input(input_data.content, input_data.title)
        return {"success": True, "data": {"id": str(item.id), "title": item.title}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch/urls", response_model=dict)
async def submit_batch_urls(
    input_data: BatchUrlInput, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit a batch of URLs for background processing"""
    processor = BatchProcessor(db)
    task = await processor.create_task("url_import", len(input_data.urls))
    
    # Start background processing
    url_strings = [str(u) for u in input_data.urls]
    background_tasks.add_task(BatchProcessor.process_urls_background, task.id, url_strings)
    
    return {"success": True, "data": {"task_id": str(task.id), "status": task.status}}

@router.post("/batch/files", response_model=dict)
async def submit_batch_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Submit a batch of files for background processing"""
    processor = BatchProcessor(db)
    task = await processor.create_task("file_import", len(files))
    
    file_paths = []
    try:
        for file in files:
            suffix = os.path.splitext(file.filename)[1] if file.filename else ""
            # Create a named temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                file_paths.append(tmp.name)
                
        # Start background processing
        background_tasks.add_task(BatchProcessor.process_files_background, task.id, file_paths)
        
    except Exception as e:
        # If setup fails, clean up immediately
        for path in file_paths:
            try:
                os.remove(path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to prepare batch upload: {str(e)}")
    
    return {"success": True, "data": {"task_id": str(task.id), "status": task.status}}

@router.get("/batch/{task_id}", response_model=dict)
async def get_batch_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get the status of a batch task"""
    processor = BatchProcessor(db)
    try:
        uuid_id = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
        
    task = await processor.get_task(uuid_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {
        "success": True, 
        "data": {
            "id": str(task.id),
            "status": task.status,
            "progress": {
                "total": task.total_items,
                "processed": task.processed_items,
                "failed": task.failed_items
            },
            "result": task.result,
            "error": task.error_message
        }
    }
