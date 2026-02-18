import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.ai.facade import ai_facade
from app.models.concept import Concept, ConceptSynonym

logger = logging.getLogger(__name__)

class ConceptExtractor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        使用 AI 从文本中提取概念。
        返回表示概念的字典列表。
        """
        if not text or len(text.strip()) == 0:
            return []

        max_chars = 10000 
        truncated_text = text[:max_chars]

        try:
            concepts = await ai_facade.extract_concepts(title="", content=truncated_text)
            
            logger.info(f"Extracted {len(concepts)} concepts from text")
            return concepts

        except Exception as e:
            logger.error(f"Error during concept extraction: {e}")
            return []

    async def save_concepts(self, concepts_data: List[Dict[str, Any]]) -> List[Concept]:
        """
        将提取的概念保存到数据库，处理去重。
        """
        saved_concepts = []
        for c_data in concepts_data:
            name = c_data.get("name")
            if not name:
                continue

            result = await self.db.execute(select(Concept).where(Concept.name == name))
            existing_concept = result.scalars().first()

            if existing_concept:
                saved_concepts.append(existing_concept)
            else:
                new_concept = Concept(
                    name=name,
                    type=c_data.get("type", "concept"),
                    description=c_data.get("description")
                )
                self.db.add(new_concept)
                saved_concepts.append(new_concept)
        
        await self.db.commit()
        for c in saved_concepts:
            await self.db.refresh(c)
            
        return saved_concepts
