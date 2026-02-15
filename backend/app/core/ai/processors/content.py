import logging
from typing import List, Dict, Any
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader
from app.schemas.ai import ContentClassificationResponse, SourceAnalyzeResponse
import uuid

logger = logging.getLogger(__name__)

class ContentProcessor:
    async def classify_content(self, title: str, content: str, existing_nodes: List[Dict[str, Any]]) -> ContentClassificationResponse:
        prompt_name = "content_classification"
        variables = {
            "title": title,
            "content": content[:2000], # Truncate for token limit
            "existing_nodes": existing_nodes
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model)
        
        if not response_text:
            raise ValueError("AI returned empty response")
            
        result = ai_client.parse_json(response_text)
        
        suggested_node_id = result.get("suggested_node_id")
        if suggested_node_id == "null":
            suggested_node_id = None
            
        return ContentClassificationResponse(
            suggested_node_id=uuid.UUID(suggested_node_id) if suggested_node_id else None,
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            tags=result.get("tags", [])
        )

    async def analyze_source(self, url: str, sample_content: str) -> SourceAnalyzeResponse:
        prompt_name = "source_analysis"
        variables = {
            "url": url,
            "content_sample": sample_content[:2000]
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model)
        
        if not response_text:
            raise ValueError("AI returned empty response")
            
        result = ai_client.parse_json(response_text)
        
        return SourceAnalyzeResponse(
            title=result.get("title", "Untitled Source"),
            summary=result.get("summary", ""),
            tags=result.get("tags", []),
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence")
        )

content_processor = ContentProcessor()
