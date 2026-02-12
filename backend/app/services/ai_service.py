from openai import AsyncOpenAI
from app.config import settings
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        if settings.SILICONFLOW_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.SILICONFLOW_API_KEY,
                base_url=settings.SILICONFLOW_BASE_URL
            )
        else:
            logger.warning("SILICONFLOW_API_KEY not set. AI Service will not function.")

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "deepseek-ai/DeepSeek-V3", temperature: float = 0.3) -> Optional[str]:
        """
        Send a chat completion request to the AI model.
        
        Args:
            messages: List of message dictionaries (role, content)
            model: Model name to use
            temperature: Sampling temperature
            
        Returns:
            The content of the response message, or None if failed
        """
        if not self.client:
            logger.error("AI Client not initialized. Cannot perform chat completion.")
            return None
        
        try:
            logger.info(f"Sending request to AI model: {model}")
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            content = response.choices[0].message.content
            logger.info("AI request successful")
            return content
        except Exception as e:
            logger.error(f"AI Service Error: {str(e)}")
            # In production, might want to raise specific exceptions or handle retries
            return None

    async def validate_content_soft(self, content: str, criteria: str) -> Dict[str, Any]:
        """
        Perform soft validation using AI.
        """
        system_prompt = "You are a content validator. Evaluate the content based on the criteria. Return JSON with 'valid' (bool) and 'reason' (str)."
        user_prompt = f"Content: {content}\nCriteria: {criteria}"
        
        response = await self.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="deepseek-ai/DeepSeek-V3" # Or a smaller model for validation
        )
        
        # Simple parsing for now, ideally use structured output or Pydantic validation
        # This is a placeholder for actual implementation
        return {"raw_response": response}

ai_service = AIService()
