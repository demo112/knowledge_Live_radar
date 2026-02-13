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

        text = (content.get("content", "") or "")[:3000]
        title = content.get("title", "") or ""
        
        try:
            result = await ai_service.validate_content_soft(title, text)
            
            score = result.get("score", 0)
            reason = result.get("reason", "")
            
            # Pass if score >= 60
            is_valid = score >= 60
            
            return is_valid, {
                "score": score,
                "reason": reason,
                "dimensions": result.get("dimensions", {})
            }
        except Exception as e:
            logger.error(f"Soft validation failed: {e}")
            return True, {"reason": "Skipped (Error)"}
