import os
import json
import logging
import asyncio
import urllib.parse
from typing import Any, Dict, List, Optional, Callable
from sqlalchemy import select, desc

from app.database import AsyncSessionLocal
from app.models.config_history import ConfigHistory

logger = logging.getLogger(__name__)

CONFIG_FILE_PATH = "system_config.json"

class ConfigurationService:
    _instance = None
    _config_cache: Dict[str, Any] = {}
    _subscribers: List[Callable[[str, Any], None]] = []
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Load defaults initially (sync)
            self._config_cache = self._get_defaults()
            self._load_from_file_sync()
            self._initialized = True

    def _get_defaults(self) -> Dict[str, Any]:
        return {
            "health.check_interval_hours": 24,
            "hotspot.emerging_threshold": 5,
            "hotspot.trending_growth_rate": 0.1,
            "hotspot.mature_growth_rate_threshold": 0.01,
            "hotspot.cooling_days_threshold": 14,
            "hotspot.archive_days_threshold": 30,
            
            "drift.similarity_threshold": 0.7,
            
            "crawl.default_timeout_seconds": 30,
            "crawl.max_retries": 3,
            
            "restructure.max_node_content": 50,
            "restructure.max_hierarchy_depth": 5,
            "restructure.max_siblings": 10,
            
            # AI configuration (Cloud/Legacy)
            "ai.api_key": "",
            "ai.base_url": "https://api.siliconflow.cn/v1",
            "ai.model": "deepseek-ai/DeepSeek-V3",
            "ai.temperature": 0.3,
            "ai.max_retries": 3,
            "ai.enabled": False,

            # AI Local configuration
            "ai.local.base_url": "http://localhost:11434/v1",
            "ai.local.model": "qwen2.5:7b",
            "ai.local.timeout": 5.0,
            "ai.local.enabled": True,

            # AI Strategy
            "ai.strategy": "local_first", # local_first, cloud_only, local_only
        }

    def _load_from_file_sync(self):
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config_cache.update(file_config)
                logger.info(f"Loaded configuration from {CONFIG_FILE_PATH}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config_cache.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        return self._config_cache.copy()
    def get_masked(self, key: str) -> Any:
        """Get configuration value with masking applied for sensitive data.

        For API keys (strings longer than 8 characters), returns masked format:
        "first4***last4"

        For other configuration items, returns the original value.

        Args:
            key: Configuration key to retrieve

        Returns:
            Masked value for sensitive strings, original value otherwise
        """
        value = self.get(key)

        # Only mask sensitive keys
        sensitive_keys = ["ai.api_key"]
        if key not in sensitive_keys and "password" not in key and "secret" not in key:
            return value

        # Only mask string values longer than 8 characters
        if isinstance(value, str) and len(value) > 8:
            return value[:4] + "***" + value[-4:]

        return value

    async def set(self, key: str, value: Any, user_id: str = "system"):
        # Skip update if value is masked (contains "***")
        if isinstance(value, str) and "***" in value:
            logger.info(f"Skipping update for {key} because value is masked")
            return

        old_value = self.get(key)
        if old_value == value:
            return

        # Validate
        self._validate(key, value)

        # Update cache
        self._config_cache[key] = value
        
        # Persist to file
        await self._save_to_file()
        
        # Record history
        await self._record_history(key, old_value, value, user_id)
        
        # Notify
        self._notify_subscribers(key, value)

    def _validate(self, key: str, value: Any):
        # Basic type validation based on defaults
        defaults = self._get_defaults()
        if key in defaults:
            expected_type = type(defaults[key])
            if not isinstance(value, expected_type) and expected_type is not type(None):
                # Allow float for int if it's a whole number, or strict?
                # Python's isinstance(1.0, int) is False.
                # Let's be a bit flexible for numbers
                if isinstance(defaults[key], (int, float)) and isinstance(value, (int, float)):
                    pass
                else:
                    raise ValueError(f"Invalid type for config key '{key}'. Expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Specific validations
        if key.endswith("_rate") or key.endswith("_threshold") or \
           key.endswith("_seconds") or key.endswith("_minutes") or \
           key.endswith("_hours") or key.endswith("_days"):
            if isinstance(value, (int, float)) and value < 0:
                  raise ValueError(f"Value for '{key}' must be non-negative")

        # AI Configuration Validation
        if key == "ai.base_url":
            result = urllib.parse.urlparse(str(value))
            if not all([result.scheme, result.netloc]):
                raise ValueError("ai.base_url must be a valid URL")
        
        if key == "ai.temperature":
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 2.0):
                raise ValueError("ai.temperature must be between 0.0 and 2.0")

        if key == "ai.max_retries":
            if not isinstance(value, int) or value <= 0:
                raise ValueError("ai.max_retries must be a positive integer")

    async def _save_to_file(self):
        try:
            def write_file():
                with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(self._config_cache, f, indent=2)
            
            await asyncio.to_thread(write_file)
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")

    async def _record_history(self, key, old, new, user):
        async with AsyncSessionLocal() as session:
            try:
                history = ConfigHistory(
                    config_key=key,
                    old_value=old,
                    new_value=new,
                    changed_by=user
                )
                session.add(history)
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to record config history: {e}")

    async def get_history(self, key: Optional[str] = None, limit: int = 50) -> List[ConfigHistory]:
        async with AsyncSessionLocal() as session:
            query = select(ConfigHistory).order_by(desc(ConfigHistory.created_at)).limit(limit)
            if key:
                query = query.filter(ConfigHistory.config_key == key)
            
            result = await session.execute(query)
            return result.scalars().all()

    async def reload(self):
        # Async reload from file
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                def read_file():
                    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                        return json.load(f)
                
                file_config = await asyncio.to_thread(read_file)
                self._config_cache.update(file_config)
                logger.info("Reloaded configuration")
            except Exception as e:
                logger.error(f"Failed to reload config file: {e}")

    def subscribe(self, callback: Callable[[str, Any], None]):
        self._subscribers.append(callback)

    def _notify_subscribers(self, key: str, value: Any):
        for callback in self._subscribers:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Error in config subscriber: {e}")

# Singleton instance
configuration_service = ConfigurationService()
