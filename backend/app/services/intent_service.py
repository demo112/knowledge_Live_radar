from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from app.core.ai.facade import ai_facade
from app.core.ai.processors.action_generator import action_generator
from app.schemas.intent import IntentParseResult, IntentResponse, IntentCreateRequest
from app.repositories.knowledge import KnowledgeNodeRepository

logger = logging.getLogger(__name__)

class IntentService:
    def __init__(self, db_session=None):
        self.db = db_session
        if db_session:
            self.knowledge_repo = KnowledgeNodeRepository(db_session)
        else:
            self.knowledge_repo = None

    async def parse_intent(self, text: str) -> IntentParseResult:
        """
        Parse user input text into structured intent using AI.
        """
        logger.info(f"Parsing intent for text: {text[:50]}...")
        result = await ai_facade.parse_intent(text)
        logger.info(f"Parsed intent: {result.intent_type} - {result.primary_topic}")
        return result

    async def process_intent(self, request: IntentCreateRequest) -> IntentResponse:
        """
        Process user intent request:
        1. Parse intent
        2. Generate suggested actions (Task 4.2)
        """
        parsed_result = await self.parse_intent(request.text)
        
        # Task 4.2: Generate actions based on intent
        actions = await action_generator.generate_actions(parsed_result)
        
        return IntentResponse(
            id="temp-id", # TODO: Generate ID or save to DB
            parsed_intent=parsed_result,
            suggested_actions=actions
        )
