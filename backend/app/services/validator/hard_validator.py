from .base import BaseValidator
from typing import Dict, Any, List, Tuple

class HardValidator(BaseValidator):
    def __init__(self, min_length: int = 10, banned_words: List[str] = None):
        self.min_length = min_length
        self.banned_words = banned_words or []

    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        text = content.get("content", "") or ""
        title = content.get("title", "") or ""
        
        details = {}
        
        if len(text) < self.min_length and len(title) < self.min_length:
            details["reason"] = "Content too short"
            return False, details
            
        full_text = (title + " " + text).lower()
        for word in self.banned_words:
            if word.lower() in full_text:
                details["reason"] = f"Contains banned word: {word}"
                return False, details
                
        return True, {"reason": "Passed hard validation"}
