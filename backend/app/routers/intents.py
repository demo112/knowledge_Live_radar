from fastapi import APIRouter, Depends, status, HTTPException
from typing import Dict, Any, List
from uuid import UUID

from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.intent_service import IntentService
from app.schemas.intent import IntentParseResult, IntentCreateRequest, IntentResponse
from app.schemas.common import SuccessResponse

router = APIRouter(
    prefix="/intents",
    tags=["Intents"]
)

def get_service(db: AsyncSession = Depends(get_db)) -> IntentService:
    return IntentService(db)

@router.post("/parse", response_model=SuccessResponse[IntentParseResult])
async def parse_intent(
    request: IntentCreateRequest,
    service: IntentService = Depends(get_service)
):
    """
    Task 4.1: Parse user intent from natural language input.
    """
    result = await service.parse_intent(request.text)
    return SuccessResponse(data=result)

@router.post("/process", response_model=SuccessResponse[IntentResponse])
async def process_intent(
    request: IntentCreateRequest,
    service: IntentService = Depends(get_service)
):
    """
    Task 4.2: Process user intent and generate actions (Pending).
    Currently just returns parsed intent.
    """
    result = await service.process_intent(request)
    return SuccessResponse(data=result)
