"""
⚠️ 已废弃 - DEPRECATED

此模块已废弃，请使用新架构 `app.core.ai`。

废弃时间: 2026-02-18
替代方案:
- 底层调用: from app.core.ai.client import ai_client
- 高级操作: from app.core.ai.facade import ai_facade

迁移指南:
- ai_service.chat_completion() → ai_client.chat_completion()
- ai_service.validate_content_soft() → ai_facade.validate_content_soft()
- ai_service.generate_summary() → ai_facade.generate_summary()
- ai_service.extract_concepts() → ai_facade.extract_concepts()
- ai_service.generate_tags() → ai_facade.generate_tags()
- ai_service._parse_json() → ai_client.parse_json()

此文件将在未来版本中移除。
"""

import warnings

warnings.warn(
    "app.services.ai_service 已废弃，请使用 app.core.ai.client 或 app.core.ai.facade",
    DeprecationWarning,
    stacklevel=2
)

from openai import AsyncOpenAI
from app.services.config.configuration_service import configuration_service
import logging
import json
import re
from typing import List, Dict, Any, Optional
from app.services.prompt.prompt_manager import PromptManager
import asyncio

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self._cloud_client = None
        self._local_client = None
        self._local_semaphore = asyncio.Semaphore(1)
        self._last_config = {}
        self._initialize_clients()
        self.prompt_manager = PromptManager()

    def _initialize_clients(self):
        cloud_enabled = configuration_service.get("ai.enabled")
        cloud_api_key = configuration_service.get("ai.api_key")
        cloud_base_url = configuration_service.get("ai.base_url")

        local_enabled = configuration_service.get("ai.local.enabled")
        local_base_url = configuration_service.get("ai.local.base_url")
        local_timeout = configuration_service.get("ai.local.timeout", 5.0)

        current_config = {
            "cloud_enabled": cloud_enabled,
            "cloud_api_key": cloud_api_key,
            "cloud_base_url": cloud_base_url,
            "local_enabled": local_enabled,
            "local_base_url": local_base_url,
            "local_timeout": local_timeout
        }

        if current_config == self._last_config and (self._cloud_client or self._local_client):
            return

        self._last_config = current_config
        
        if cloud_enabled and cloud_api_key:
            try:
                self._cloud_client = AsyncOpenAI(
                    api_key=cloud_api_key,
                    base_url=cloud_base_url
                )
            except Exception as e:
                logger.error(f"Failed to initialize Cloud AI client: {e}")
                self._cloud_client = None
        else:
            self._cloud_client = None
            if cloud_enabled:
                 logger.warning("Cloud AI enabled but API Key not set.")

        if local_enabled:
            try:
                self._local_client = AsyncOpenAI(
                    api_key="ollama",
                    base_url=local_base_url,
                    timeout=local_timeout
                )
            except Exception as e:
                logger.error(f"Failed to initialize Local AI client: {e}")
                self._local_client = None
        else:
            self._local_client = None

    @property
    def client(self):
        self._initialize_clients()
        return self._cloud_client if self._cloud_client else self._local_client

    async def chat_completion(self, messages: List[Dict[str, Any]], model: Optional[str] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None) -> Optional[str]:
        self._initialize_clients()
        
        strategy = configuration_service.get("ai.strategy", "local_first")
        
        temperature = temperature if temperature is not None else configuration_service.get("ai.temperature")
        max_retries = max_retries if max_retries is not None else configuration_service.get("ai.max_retries")

        if strategy == "cloud_only":
            return await self._call_cloud(messages, model, temperature, max_retries)
        elif strategy == "local_only":
            return await self._call_local(messages, model, temperature, max_retries)
        else:
            try:
                result = await self._call_local(messages, model, temperature, max_retries)
                if result:
                    return result
                logger.warning("Local LLM returned None, falling back to Cloud...")
                return await self._call_cloud(messages, model, temperature, max_retries)
            except Exception as e:
                logger.warning(f"Local LLM failed ({type(e).__name__}: {e}), falling back to Cloud...")
                return await self._call_cloud(messages, model, temperature, max_retries)

    async def _call_local(self, messages, model, temperature, max_retries):
        if not self._local_client:
            if configuration_service.get("ai.strategy") == "local_only":
                logger.error("Local AI not initialized but strategy is local_only.")
            raise ValueError("Local client not initialized")
            
        target_model = model or configuration_service.get("ai.local.model")
        
        async with self._local_semaphore:
            try:
                logger.info(f"Sending request to Local LLM: {target_model}")
                response = await self._local_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                raise e

    async def _call_cloud(self, messages, model, temperature, max_retries):
        if not self._cloud_client:
            if configuration_service.get("ai.enabled"):
                logger.error("Cloud AI not initialized.")
            return None
            
        target_model = model or configuration_service.get("ai.model")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to Cloud LLM: {target_model} (attempt {attempt + 1}/{max_retries})")
                response = await self._cloud_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                is_retryable = any(kw in error_str.lower() for kw in ["timeout", "rate", "429", "500", "502", "503", "connection"])
                
                if not is_retryable or attempt == max_retries - 1:
                    logger.error(f"Cloud AI Error (final): {error_str}")
                    return None
                
                delay = (2 ** attempt) * 1.0
                if "429" in error_str or "rate" in error_str.lower():
                    delay = (3 ** attempt) * 1.0
                
                logger.warning(f"Cloud AI Error (retrying in {delay}s): {error_str}")
                await asyncio.sleep(delay)
        return None

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
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
        if not (self._cloud_client or self._local_client) and not (configuration_service.get("ai.enabled") or configuration_service.get("ai.local.enabled")):
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
        if not (self._cloud_client or self._local_client) and not (configuration_service.get("ai.enabled") or configuration_service.get("ai.local.enabled")):
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
        
        if not response:
            return {"summary": "", "key_points": []}
            
        result = self._parse_json(response)
        
        if not result and response:
            return {"summary": response.strip(), "key_points": []}
            
        return result

    async def extract_concepts(self, title: str, content: str) -> List[Dict[str, str]]:
        if not (self._cloud_client or self._local_client) and not (configuration_service.get("ai.enabled") or configuration_service.get("ai.local.enabled")):
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
        if not (self._cloud_client or self._local_client) and not (configuration_service.get("ai.enabled") or configuration_service.get("ai.local.enabled")):
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
