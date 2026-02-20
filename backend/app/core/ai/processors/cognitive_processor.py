from typing import Dict, Any, List
import json
import logging
from app.core.ai.client import ai_client

logger = logging.getLogger(__name__)

class CognitiveProcessor:
    async def generate_cognitive_model(
        self, 
        name: str, 
        description: str, 
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a structured cognitive model for a concept.
        """
        prompt = f"""
        You are an expert knowledge engineer. Create a structured cognitive model for the following concept:
        
        Concept Name: {name}
        Description: {description}
        Context: {context}
        
        The cognitive model should be a JSON object with the following structure:
        {{
            "definition": "A clear, concise definition of the concept.",
            "key_attributes": ["attribute 1", "attribute 2", ...],
            "related_concepts": ["related concept 1", "related concept 2", ...],
            "misconceptions": ["common misconception 1", ...],
            "evolution_path": ["potential next step 1", "potential next step 2", ...]
        }}
        
        Return ONLY the JSON object.
        """
        
        response = await ai_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that generates structured knowledge models."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
    async def evolve_cognitive_model(
        self,
        current_model: Dict[str, Any],
        new_content_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evolve an existing cognitive model based on new content.
        """
        content_summary = "\n".join([
            f"- {item.get('title', '')}: {item.get('summary', '')}" 
            for item in new_content_items
        ])
        
        prompt = f"""
        You are an expert knowledge engineer. Evolve the following cognitive model based on new information.
        
        Current Cognitive Model:
        {json.dumps(current_model, indent=2)}
        
        New Information:
        {content_summary}
        
        Tasks:
        1. Refine the definition if the new information provides better clarity.
        2. Add new key attributes if discovered.
        3. Update related concepts.
        4. Identify new misconceptions or evolution paths.
        5. Keep the structure consistent.
        
        Return ONLY the updated JSON object.
        """
        
        response = await ai_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that evolves knowledge models."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return ai_client.parse_json(response)

cognitive_processor = CognitiveProcessor()
