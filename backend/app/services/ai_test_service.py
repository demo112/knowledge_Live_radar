import logging
import time
from typing import Dict, Any
from openai import AsyncOpenAI
from app.services.config.configuration_service import configuration_service

logger = logging.getLogger(__name__)

class AITestService:
    def __init__(self):
        """
        Initialize AITestService.
        Relies on the singleton configuration_service for settings.
        """
        pass

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to AI provider using current configuration.
        
        Returns:
            Dict containing:
            - success: bool
            - message: str
            - latency_ms: float (optional)
            - model: str (optional)
            - code: str (optional, for errors)
        """
        enabled = configuration_service.get("ai.enabled")
        api_key = configuration_service.get("ai.api_key")
        base_url = configuration_service.get("ai.base_url")
        model = configuration_service.get("ai.model")

        if not enabled:
            return {
                "success": False,
                "message": "AI功能已禁用",
                "code": "AI_DISABLED"
            }

        if not api_key:
             return {
                "success": False,
                "message": "未配置 API Key",
                "code": "API_KEY_MISSING"
            }

        # Create a temporary client for testing
        try:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=10.0, # 10 seconds timeout as required
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
            await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            latency = (time.time() - start_time) * 1000 # ms
            
            return {
                "success": True,
                "latency_ms": round(latency, 2),
                "model": model,
                "message": "连接测试成功"
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
