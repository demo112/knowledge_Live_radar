from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.content import ContentItem
from app.models.approval import Approval
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from app.schemas.content_input import UrlInput, TextInput, AnalysisRequest
from app.schemas.approval import ApprovalResponse
from app.services.input_processor import InputProcessor
from app.services.content_analyzer import ContentAnalyzer
from app.schemas.content import ContentResponse
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Remove local ContentResponse definition as we now import it
# class ContentResponse(BaseModel):
#     id: UUID
#     title: str
#     url: str
#     summary: Optional[str] = None
#     publish_time: Optional[datetime] = None
#     status: str
#     created_at: datetime
#     
#     model_config = ConfigDict(from_attributes=True)

router = APIRouter(prefix="/contents", tags=["contents"])

@router.get("", response_model=PaginatedResponse[ContentResponse])
async def get_contents(
    skip: int = 0,
    limit: int = 20,
    source_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentItem).order_by(desc(ContentItem.created_at)).offset(skip).limit(limit)
    if source_id:
        stmt = stmt.where(ContentItem.source_id == source_id)
        
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    total = len(items) # Should execute count query separately for real pagination
    
    return PaginatedResponse(data=PaginatedData(items=items, total=total, page=skip//limit + 1, page_size=limit))

@router.get("/{id}", response_model=SuccessResponse[ContentResponse])
async def get_content(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ContentItem).where(ContentItem.id == id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return SuccessResponse(data=content)

@router.post("/upload", response_model=SuccessResponse[ContentResponse])
async def upload_file(
    file: UploadFile = File(...),
    submitter_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    processor = InputProcessor(db)
    content = await processor.process_file_input(file, submitter_id)
    return SuccessResponse(data=content)

@router.post("/url", response_model=SuccessResponse[ContentResponse])
async def submit_url(
    input: UrlInput,
    db: AsyncSession = Depends(get_db)
):
    processor = InputProcessor(db)
    content = await processor.process_url_input(input.url, input.submitter_id)
    return SuccessResponse(data=content)

@router.post("/text", response_model=SuccessResponse[ContentResponse])
async def submit_text(
    input: TextInput,
    db: AsyncSession = Depends(get_db)
):
    processor = InputProcessor(db)
    content = await processor.process_text_input(input.text, input.title, input.submitter_id)
    return SuccessResponse(data=content)

@router.post("/{id}/analyze", response_model=SuccessResponse[List[ApprovalResponse]])
async def analyze_content(
    id: UUID,
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    analyzer = ContentAnalyzer(db)
    try:
        pyramid_id_uuid = UUID(request.pyramid_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pyramid_id format")
        
    proposals = await analyzer.analyze_content(id, pyramid_id_uuid)
    return SuccessResponse(data=proposals)
