from openai import AsyncOpenAI
from app.services.config.configuration_service import configuration_service
import logging
import json
import re
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.ai_metric import AIMetric
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self._cloud_client = None
        self._local_client = None
        self._local_semaphore = asyncio.Semaphore(1)  # Limit local concurrency
        self._last_config = {}
        self._initialize_clients()

    async def _save_metric(self, metric_data: Dict[str, Any]):
        try:
            async with AsyncSessionLocal() as session:
                metric = AIMetric(**metric_data)
                session.add(metric)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save AI metric: {e}")

    def _record_metric(self, start_time: float, model: str, provider: str, 
                       module: str, response: Any = None, error: Exception = None):
        try:
            latency = time.time() - start_time
            status = "error" if error else "success"
            error_message = str(error) if error else None
            
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
            if response and hasattr(response, 'usage') and response.usage:
                prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                total_tokens = getattr(response.usage, 'total_tokens', 0)
                
            metric_data = {
                "timestamp": datetime.now(),
                "module": module,
                "model": model,
                "provider": provider,
                "latency": latency,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "status": status,
                "error_message": error_message
            }
            
            asyncio.create_task(self._save_metric(metric_data))
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")

    def _initialize_clients(self):
        # Fetch current config
        cloud_enabled = configuration_service.get("ai.enabled")
        cloud_api_key = configuration_service.get("ai.api_key")
        cloud_base_url = configuration_service.get("ai.base_url")
        cloud_timeout = configuration_service.get("ai.timeout", 60.0)

        local_enabled = configuration_service.get("ai.local.enabled")
        local_base_url = configuration_service.get("ai.local.base_url")
        local_timeout = configuration_service.get("ai.local.timeout", 5.0)

        current_config = {
            "cloud_enabled": cloud_enabled,
            "cloud_api_key": cloud_api_key,
            "cloud_base_url": cloud_base_url,
            "cloud_timeout": cloud_timeout,
            "local_enabled": local_enabled,
            "local_base_url": local_base_url,
            "local_timeout": local_timeout
        }

        # Only re-initialize if config changed
        if current_config == self._last_config and (self._cloud_client or self._local_client):
            return

        self._last_config = current_config
        
        # Initialize Cloud Client
        if cloud_enabled and cloud_api_key:
            try:
                self._cloud_client = AsyncOpenAI(
                    api_key=cloud_api_key,
                    base_url=cloud_base_url,
                    timeout=cloud_timeout
                )
            except Exception as e:
                logger.error(f"Failed to initialize Cloud AI client: {e}")
                self._cloud_client = None
        else:
            self._cloud_client = None
            if cloud_enabled:
                 logger.warning("Cloud AI enabled but API Key not set.")

        # Initialize Local Client
        if local_enabled:
            try:
                self._local_client = AsyncOpenAI(
                    api_key="ollama", # Ollama doesn't strictly need a key
                    base_url=local_base_url,
                    timeout=local_timeout # Set global timeout for local client
                )
            except Exception as e:
                logger.error(f"Failed to initialize Local AI client: {e}")
                self._local_client = None
        else:
            self._local_client = None

    async def chat_completion(self, messages: List[Dict[str, Any]], model: Optional[str] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None, context: str = "unknown", **kwargs) -> Optional[str]:
        """
        Send a chat completion request with strategy-based routing and fallback.
        """
        self._initialize_clients()
        
        strategy = configuration_service.get("ai.strategy", "local_first")
        
        # Defaults
        temperature = temperature if temperature is not None else configuration_service.get("ai.temperature")
        max_retries = max_retries if max_retries is not None else configuration_service.get("ai.max_retries")

        if strategy == "cloud_only":
            return await self._call_cloud(messages, model, temperature, max_retries, context, **kwargs)
        elif strategy == "local_only":
            return await self._call_local(messages, model, temperature, max_retries, context, **kwargs)
        else: # local_first
            try:
                # Try local first
                result = await self._call_local(messages, model, temperature, max_retries, context, **kwargs)
                if result:
                    return result
                # If result is None (handled error inside _call_local but returned None), fallback
                logger.warning("Local LLM returned None, falling back to Cloud...")
                return await self._call_cloud(messages, model, temperature, max_retries, context, **kwargs)
            except Exception as e:
                logger.warning(f"Local LLM failed ({type(e).__name__}: {e}), falling back to Cloud...")
                return await self._call_cloud(messages, model, temperature, max_retries, context, **kwargs)

    async def _call_local(self, messages, model, temperature, max_retries, context: str = "unknown", **kwargs):
        if not self._local_client:
            if configuration_service.get("ai.strategy") == "local_only":
                logger.error("Local AI not initialized but strategy is local_only.")
            # If local_first, returning None triggers fallback in caller if we caught it, 
            # but raising exception is better for clarity
            raise ValueError("Local client not initialized")
            
        target_model = model or configuration_service.get("ai.local.model")
        start_time = time.time()
        
        # Use semaphore for local concurrency
        async with self._local_semaphore:
            try:
                logger.info(f"Sending request to Local LLM: {target_model}")
                response = await self._local_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    **kwargs
                )
                self._record_metric(start_time, target_model, "local", context, response=response)
                return response.choices[0].message.content
            except Exception as e:
                self._record_metric(start_time, target_model, "local", context, error=e)
                # Re-raise to trigger fallback
                raise e

    async def _call_cloud(self, messages, model, temperature, max_retries, context: str = "unknown", **kwargs):
        if not self._cloud_client:
            if configuration_service.get("ai.enabled"):
                logger.error("Cloud AI not initialized.")
            return None
            
        target_model = model or configuration_service.get("ai.model")
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                logger.info(f"Sending request to Cloud LLM: {target_model} (attempt {attempt + 1}/{max_retries})")
                response = await self._cloud_client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    **kwargs
                )
                self._record_metric(start_time, target_model, "cloud", context, response=response)
                return response.choices[0].message.content
            except Exception as e:
                self._record_metric(start_time, target_model, "cloud", context, error=e)
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

    def parse_json(self, text: str) -> Dict[str, Any]:
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

    async def audio_transcriptions(self, file_path: str, model: Optional[str] = None, context: str = "unknown", **kwargs) -> str:
        """
        Transcribe audio file using Cloud AI (SiliconFlow/OpenAI compatible).
        """
        self._initialize_clients()
        
        if not self._cloud_client:
            if configuration_service.get("ai.enabled"):
                logger.error("Cloud AI not initialized.")
            raise RuntimeError("Cloud AI not initialized")
            
        target_model = model or configuration_service.get("ai.audio_model", "whisper-1")
        start_time = time.time()
        
        try:
            logger.info(f"Sending audio transcription request: {target_model}")
            
            # Using standard open in async context is generally discouraged for I/O but acceptable for small-medium files in MVP.
            # For high concurrency, consider aiofiles or run_in_executor.
            with open(file_path, "rb") as audio_file:
                response = await self._cloud_client.audio.transcriptions.create(
                    model=target_model,
                    file=audio_file,
                    **kwargs
                )
            
            # Record metric (Transcription object usually doesn't have token usage, but _record_metric handles missing usage)
            self._record_metric(start_time, target_model, "cloud", context, response=response)
            
            return response.text
            
        except Exception as e:
            self._record_metric(start_time, target_model, "cloud", context, error=e)
            logger.error(f"Audio Transcription Error: {e}")
            raise e

ai_client = AIClient()
