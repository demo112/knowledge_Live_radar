import logging
from typing import Optional
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader
from app.schemas.ai import PyramidNodeStructure, PyramidSuggestResponse, NodePlacementResponse
import uuid

logger = logging.getLogger(__name__)

class PyramidProcessor:
    async def find_best_parent_node(
        self,
        new_node_name: str,
        new_node_description: str,
        source_context: str,
        candidate_nodes: list[dict]
    ) -> NodePlacementResponse:
        """
        Find the best parent node for a new node.
        """
        prompt_name = "approval/node_placement"
        variables = {
            "new_node_name": new_node_name,
            "new_node_description": new_node_description,
            "source_context": source_context,
            "candidate_nodes": candidate_nodes
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, context="node_placement")
        
        if not response_text:
            raise ValueError("AI returned empty response")
            
        result = ai_client.parse_json(response_text)
        
        if not result:
             logger.error(f"Invalid AI response for node placement: {response_text}")
             raise ValueError("Failed to parse node placement from AI response")

        try:
            return NodePlacementResponse(**result)
        except Exception as e:
            logger.error(f"Pydantic validation failed for node placement: {e}")
            raise ValueError("AI response did not match expected node placement schema")

    async def generate_structure(self, name: str, description: str) -> PyramidSuggestResponse:
        """
        Generate a pyramid structure based on name and description.
        """
        prompt_name = "pyramid/structure"
        variables = {
            "name": name,
            "description": description
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            raise ValueError(f"Failed to load prompt: {prompt_name}")
            
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, context="pyramid_structure")
        
        if not response_text:
            raise ValueError("AI returned empty response")
            
        result = ai_client.parse_json(response_text)
        
        if not result or "structure" not in result:
             # Fallback or error handling
             logger.error(f"Invalid AI response for pyramid structure: {response_text}")
             raise ValueError("Failed to parse pyramid structure from AI response")

        structure_data = result["structure"]
        reasoning = result.get("reasoning")
        
        # Validate with Pydantic
        try:
            structure = PyramidNodeStructure(**structure_data)
        except Exception as e:
            logger.error(f"Pydantic validation failed for pyramid structure: {e}")
            raise ValueError("AI response did not match expected structure schema")

        return PyramidSuggestResponse(
            suggestion_id=uuid.uuid4(),
            structure=structure,
            reasoning=reasoning,
            confidence=0.9 # Placeholder, AI might not return confidence for structure
        )

pyramid_processor = PyramidProcessor()
