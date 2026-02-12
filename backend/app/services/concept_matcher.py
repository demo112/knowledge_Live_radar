import logging
import uuid
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.pyramid import PyramidNode
from app.models.concept import Concept, ConceptSynonym

logger = logging.getLogger(__name__)

class MatchType(str, Enum):
    EXACT = "exact"
    SYNONYM = "synonym"
    NEW = "new"
    UNCERTAIN = "uncertain"

@dataclass
class MatchResult:
    concept_id: uuid.UUID
    match_type: MatchType
    node_id: Optional[uuid.UUID] = None
    confidence: float = 0.0
    details: Optional[str] = None

class ConceptMatcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def match_concept(self, concept: Concept, pyramid_id: uuid.UUID) -> MatchResult:
        """
        Match a concept against nodes in a specific pyramid.
        """
        # 1. Exact Match (Case Insensitive)
        stmt = select(PyramidNode).where(
            PyramidNode.pyramid_id == pyramid_id,
            PyramidNode.name.ilike(concept.name)
        )
        result = await self.db.execute(stmt)
        node = result.scalars().first()

        if node:
            return MatchResult(
                concept_id=concept.id,
                match_type=MatchType.EXACT,
                node_id=node.id,
                confidence=1.0,
                details=f"Exact match with node '{node.name}'"
            )

        # 2. Synonym Match
        # Check if concept name is a synonym for any node? 
        # Ideally nodes should also have synonyms, but for now we might check if 
        # any known synonym of the concept matches a node name.
        
        # Load synonyms for this concept
        stmt_synonyms = select(ConceptSynonym).where(ConceptSynonym.concept_id == concept.id)
        result_synonyms = await self.db.execute(stmt_synonyms)
        synonyms = result_synonyms.scalars().all()
        
        for syn in synonyms:
             stmt = select(PyramidNode).where(
                PyramidNode.pyramid_id == pyramid_id,
                PyramidNode.name.ilike(syn.synonym)
            )
             result = await self.db.execute(stmt)
             node = result.scalars().first()
             if node:
                 return MatchResult(
                    concept_id=concept.id,
                    match_type=MatchType.SYNONYM,
                    node_id=node.id,
                    confidence=0.9,
                    details=f"Matched via synonym '{syn.synonym}' to node '{node.name}'"
                )

        # 3. New Concept (No match found)
        return MatchResult(
            concept_id=concept.id,
            match_type=MatchType.NEW,
            confidence=0.0,
            details="No matching node found"
        )

    async def batch_match(self, concepts: List[Concept], pyramid_id: uuid.UUID) -> List[MatchResult]:
        results = []
        for concept in concepts:
            result = await self.match_concept(concept, pyramid_id)
            results.append(result)
        return results
