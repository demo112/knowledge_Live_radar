import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.ai_service import ai_service
from app.models.concept import Concept, ConceptSynonym

logger = logging.getLogger(__name__)

class ConceptExtractor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract concepts from text using AI.
        Returns a list of dictionaries representing concepts.
        """
        if not text or len(text.strip()) == 0:
            return []

        # Truncate text if too long to fit in context window (simple truncation for now)
        max_chars = 10000 
        truncated_text = text[:max_chars]

        system_prompt = """
You are a Knowledge Graph Expert. Your task is to extract key concepts from the provided text to build a knowledge pyramid.
Focus on extracting:
1. Technologies (e.g., Python, React, Docker)
2. Tools (e.g., VS Code, Git, Jira)
3. Methods/Practices (e.g., Agile, TDD, CI/CD)
4. Organizations/Companies (e.g., Google, OpenAI)
5. Core Concepts (e.g., Machine Learning, Knowledge Graph)

Return the result as a strictly valid JSON object with a single key "concepts", which is a list of objects.
Each object must have:
- "name": The canonical name of the concept (string, Title Case)
- "type": One of ["technology", "tool", "method", "organization", "concept"]
- "description": A concise description based on the text (string, max 20 words)
- "confidence": A float between 0.0 and 1.0 indicating your confidence

Example output:
{
  "concepts": [
    {"name": "Python", "type": "technology", "description": "A high-level programming language.", "confidence": 0.98},
    {"name": "TDD", "type": "method", "description": "Test Driven Development practice.", "confidence": 0.95}
  ]
}
Do not include any markdown formatting (like ```json) in the response. Just the raw JSON string.
"""
        
        user_prompt = f"Text to analyze:\n{truncated_text}"

        try:
            response = await ai_service.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1 # Low temperature for consistent JSON output
            )

            if not response:
                logger.warning("AI service returned no response for concept extraction")
                return []

            # Clean response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            concepts = data.get("concepts", [])
            
            logger.info(f"Extracted {len(concepts)} concepts from text")
            return concepts

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}. Response: {response}")
            return []
        except Exception as e:
            logger.error(f"Error during concept extraction: {e}")
            return []

    async def save_concepts(self, concepts_data: List[Dict[str, Any]]) -> List[Concept]:
        """
        Save extracted concepts to the database, handling deduplication.
        """
        saved_concepts = []
        for c_data in concepts_data:
            name = c_data.get("name")
            if not name:
                continue

            # Check if concept already exists (case-insensitive)
            # This is a basic check. In production, we might want more sophisticated matching or caching.
            result = await self.db.execute(select(Concept).where(Concept.name == name))
            existing_concept = result.scalars().first()

            if existing_concept:
                saved_concepts.append(existing_concept)
                # Optional: Update description or confidence if new one is better?
                # For now, we skip updating to preserve existing definitions.
            else:
                new_concept = Concept(
                    name=name,
                    type=c_data.get("type", "concept"),
                    description=c_data.get("description")
                )
                self.db.add(new_concept)
                saved_concepts.append(new_concept)
        
        await self.db.commit()
        # Refresh to get IDs
        for c in saved_concepts:
            await self.db.refresh(c)
            
        return saved_concepts
