from openai import AsyncOpenAI
from app.config import settings
import logging
import json
import re
from typing import List, Dict, Any, Optional
from app.services.prompt.prompt_manager import PromptManager

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
        
        self.prompt_manager = PromptManager()

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "deepseek-ai/DeepSeek-V3", temperature: float = 0.3) -> Optional[str]:
        """
        Send a chat completion request to the AI model.
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
            return None

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from text."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting from code blocks
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            # Try finding first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse JSON from AI response: {text[:100]}...")
            return {}

    async def validate_content_soft(self, title: str, content: str) -> Dict[str, Any]:
        """Soft validation using prompt template."""
        prompt = await self.prompt_manager.get_prompt_for_scene(
            "soft_validation", 
            {"title": title, "content": content}
        )
        if not prompt:
            logger.error("Prompt template 'soft_validation' not found")
            return {"score": 0, "reason": "System error: prompt missing"}

        response = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        if not response:
            return {"score": 0, "reason": "AI service failure"}
            
        result = self._parse_json(response)
        if "score" not in result:
            result["score"] = 0
            result["reason"] = result.get("reason", "Failed to parse AI score")
            
        return result

    async def generate_summary(self, title: str, content: str) -> Dict[str, Any]:
        """Generate summary using prompt template."""
        prompt = await self.prompt_manager.get_prompt_for_scene(
            "summary_generation",
            {"title": title, "content": content}
        )
        if not prompt:
            return {"summary": "", "key_points": []}

        response = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return self._parse_json(response) if response else {}

    async def extract_concepts(self, title: str, content: str) -> List[Dict[str, str]]:
        """Extract concepts using prompt template."""
        prompt = await self.prompt_manager.get_prompt_for_scene(
            "concept_extraction",
            {"title": title, "content": content}
        )
        if not prompt:
            return []

        response = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = self._parse_json(response) if response else {}
        return result.get("concepts", [])

    async def generate_tags(self, title: str, content: str) -> List[str]:
        """Generate tags using prompt template."""
        prompt = await self.prompt_manager.get_prompt_for_scene(
            "tag_generation",
            {"title": title, "content": content}
        )
        if not prompt:
            return []

        response = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = self._parse_json(response) if response else {}
        return result.get("tags", [])


ai_service = AIService()
