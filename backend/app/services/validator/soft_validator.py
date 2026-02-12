from .base import BaseValidator
from app.services.ai_service import ai_service
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SoftValidator(BaseValidator):
    def __init__(self, criteria: str = "Is this content relevant to technology, AI, or software development?"):
        self.criteria = criteria

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not ai_service.client:
            logger.warning("AI Service unavailable, skipping soft validation")
            return True, {"reason": "Skipped (AI unavailable)"}

        text = (content.get("content", "") or "")[:1000]
        title = content.get("title", "") or ""
        
        try:
            result = await ai_service.validate_content_soft(f"Title: {title}\nContent: {text}", self.criteria)
            raw_response = result.get("raw_response", "")
            
            # Simple heuristic check for now
            is_valid = "valid" in raw_response.lower() or "yes" in raw_response.lower() or "true" in raw_response.lower()
            return is_valid, {"raw_response": raw_response}
        except Exception as e:
            logger.error(f"Soft validation failed: {e}")
            return True, {"reason": "Skipped (Error)"}
