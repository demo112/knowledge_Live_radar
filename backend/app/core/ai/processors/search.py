import logging
from typing import Dict, Any
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class SearchProcessor:
    async def understand_intent(self, query: str) -> Dict[str, Any]:
        prompt_name = "search_intent"
        variables = {
            "query": query
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, context="search_intent")
        
        if not response_text:
            return {"intent": "keyword_search", "keywords": [query], "expanded_terms": []}
            
        result = ai_client.parse_json(response_text)
        return result

search_processor = SearchProcessor()
