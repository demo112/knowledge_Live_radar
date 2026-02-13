from openai import AsyncOpenAI
from app.services.config.configuration_service import configuration_service
import logging
import json
import re
from typing import List, Dict, Any, Optional
from app.services.prompt.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self._client = None
        self._last_config = {}
        self._initialize_client()
        self.prompt_manager = PromptManager()

    def _initialize_client(self):
        enabled = configuration_service.get("ai.enabled")
        api_key = configuration_service.get("ai.api_key")
        base_url = configuration_service.get("ai.base_url")
        
        current_config = {
            "enabled": enabled,
            "api_key": api_key,
            "base_url": base_url
        }
        
        # Only re-initialize if config changed
        if current_config == self._last_config and self._client is not None:
            return

        self._last_config = current_config
        
        if not enabled:
            self._client = None
            return

        if api_key:
            try:
                self._client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {e}")
                self._client = None
        else:
            # Only warn if enabled but no key
            if enabled:
                logger.warning("AI enabled but API Key not set. AI Service will not function.")
            self._client = None

    @property
    def client(self):
        self._initialize_client()
        return self._client

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None) -> Optional[str]:
        """
        Send a chat completion request with exponential backoff retry.
        """
        # Load defaults from config if not provided
        model = model or configuration_service.get("ai.model")
        temperature = temperature if temperature is not None else configuration_service.get("ai.temperature")
        max_retries = max_retries if max_retries is not None else configuration_service.get("ai.max_retries")

        if not self.client:
            if not configuration_service.get("ai.enabled"):
                logger.debug("AI Service is disabled. Skipping chat completion.")
            else:
                logger.error("AI Client not initialized. Cannot perform chat completion.")
            return None
        
        import asyncio
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to AI model: {model} (attempt {attempt + 1}/{max_retries})")
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                content = response.choices[0].message.content
                logger.info("AI request successful")
                return content
            except Exception as e:
                error_str = str(e)
                is_retryable = any(kw in error_str.lower() for kw in ["timeout", "rate", "429", "500", "502", "503", "connection"])
                
                if not is_retryable or attempt == max_retries - 1:
                    logger.error(f"AI Service Error (final): {error_str}")
                    return None
                
                delay = (2 ** attempt) * 1.0  # 1s, 2s, 4s
                if "429" in error_str or "rate" in error_str.lower():
                    delay = (3 ** attempt) * 1.0  # More aggressive backoff for rate limits
                
                logger.warning(f"AI Service Error (retrying in {delay}s): {error_str}")
                await asyncio.sleep(delay)

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
        if not self.client and not configuration_service.get("ai.enabled"):
            return {"score": 100, "reason": "Skipped (AI disabled)"}

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
        if not self.client and not configuration_service.get("ai.enabled"):
            return {"summary": "", "key_points": []}

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
        if not self.client and not configuration_service.get("ai.enabled"):
            return []

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
        if not self.client and not configuration_service.get("ai.enabled"):
            return []

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
