import logging
from typing import Dict, Any, List
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class DiscoveryProcessor:
    async def generate_adaptive_queries(self, pyramid_name: str, pyramid_structure_text: str) -> List[Dict[str, str]]:
        """
        Generate adaptive search queries based on pyramid structure context.
        """
        prompt_name = "discovery/adaptive_query_generation"
        variables = {
            "pyramid_name": pyramid_name,
            "pyramid_structure_text": pyramid_structure_text
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(
            messages, 
            model=model, 
            context="discovery_query_generation",
            temperature=metadata.get("temperature", 0.7)
        )
        
        if not response_text:
            logger.warning("AI returned empty response for adaptive query generation")
            return []
            
        try:
            result = ai_client.parse_json(response_text)
            if isinstance(result, list):
                return result
            logger.warning(f"Unexpected result format: {type(result)}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return []

discovery_processor = DiscoveryProcessor()
