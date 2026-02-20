import logging
import time
from typing import Dict, Any
from openai import AsyncOpenAI
from app.services.config.configuration_service import configuration_service
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class AITestService:
    def __init__(self):
        """
        Initialize AITestService.
        Relies on the singleton configuration_service for settings.
        """
        pass

    async def test_connection(self, target: str = "auto") -> Dict[str, Any]:
        """
        Test connection to AI provider using current configuration.
        Respects ai.strategy to determine which service to test.
        """
        enabled = configuration_service.get("ai.enabled")
        strategy = configuration_service.get("ai.strategy") or "cloud_only"
        
        # Determine target config based on strategy or explicit target
        if target == "local":
            use_local = True
        elif target == "cloud":
            use_local = False
        else:
            # For 'local_first' or 'local_only', we prioritize testing local
            use_local = strategy in ["local_first", "local_only"]
        
        if use_local:
            api_key = "ollama" # Local usually doesn't need key
            base_url = configuration_service.get("ai.local.base_url")
            model = configuration_service.get("ai.local.model")
            timeout = float(configuration_service.get("ai.local.timeout") or 30.0)
        else:
            api_key = configuration_service.get("ai.api_key")
            base_url = configuration_service.get("ai.base_url")
            model = configuration_service.get("ai.model")
            timeout = float(configuration_service.get("ai.timeout") or 60.0)

        if not enabled:
            return {
                "success": False,
                "message": "AI功能已禁用",
                "code": "AI_DISABLED"
            }

        if not api_key and not use_local:
             return {
                "success": False,
                "message": "未配置 API Key",
                "code": "API_KEY_MISSING"
            }
            
        if not base_url:
             return {
                "success": False,
                "message": "未配置 Base URL",
                "code": "URL_MISSING"
            }

        # Create a temporary client for testing
        try:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout, 
                max_retries=0 # No retries for test
            )
        except Exception as e:
            logger.error(f"Failed to initialize AI client for testing: {e}")
            return {
                "success": False,
                "message": f"客户端初始化失败: {str(e)}",
                "code": "INIT_FAILED"
            }

        start_time = time.time()
        try:
            # Send simple test request
            test_content = await prompt_loader.get_prompt("system/connectivity_test")
            if not test_content:
                logger.error("Failed to load test prompt 'system/connectivity_test'")
                raise ValueError("Test Prompt configuration missing")
                
            await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": test_content}],
                max_tokens=10
            )
            
            latency = (time.time() - start_time) * 1000 # ms
            
            target_name = "Local AI" if use_local else "Cloud AI"
            return {
                "success": True,
                "latency_ms": round(latency, 2),
                "model": model,
                "message": f"{target_name} 连接测试成功"
            }
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            error_msg = str(e)
            logger.warning(f"AI Connection test failed: {error_msg}")
            
            return {
                "success": False,
                "latency_ms": round(latency, 2),
                "model": model,
                "message": f"连接失败: {error_msg}",
                "code": "CONNECTION_FAILED"
            }
