import logging
from typing import Dict, Any, Optional
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader
from app.schemas.intent import IntentParseResult, IntentType

logger = logging.getLogger(__name__)

class IntentProcessor:
    async def parse_intent(self, text: str) -> IntentParseResult:
        """
        Parse user input into structured intent.
        """
        prompt_name = "intent/parse"
        variables = {
            "text": text
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            logger.error(f"Failed to load prompt: {prompt_name}")
            # Fallback to general intent if prompt loading fails
            return IntentParseResult(
                original_text=text,
                intent_type=IntentType.GENERAL,
                primary_topic="Unknown",
                confidence=0.0
            )
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        try:
            response_text = await ai_client.chat_completion(messages, model=model, context="intent_parse")
            
            if not response_text:
                return IntentParseResult(
                    original_text=text,
                    intent_type=IntentType.GENERAL,
                    primary_topic="Unknown",
                    confidence=0.0
                )
                
            result_dict = ai_client.parse_json(response_text)
            
            # Ensure required fields are present
            if "original_text" not in result_dict:
                result_dict["original_text"] = text
                
            return IntentParseResult(**result_dict)
            
        except Exception as e:
            logger.error(f"Error parsing intent: {e}")
            return IntentParseResult(
                original_text=text,
                intent_type=IntentType.GENERAL,
                primary_topic="Error",
                confidence=0.0
            )

intent_processor = IntentProcessor()
