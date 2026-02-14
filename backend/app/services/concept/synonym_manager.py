from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from app.models.synonym import SynonymMapping
import uuid

class SynonymManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_synonym(self, canonical_term: str, synonym: str, source: str = "manual", confidence: float = 1.0) -> SynonymMapping:
        """Add a new synonym mapping."""
        # Check if exists
        existing = await self.get_mapping(synonym)
        if existing:
            if existing.canonical_term == canonical_term:
                return existing
            # If exists but points to different term, we might need a policy. 
            # For now, we update it if the new confidence is higher or source is manual.
            if source == "manual" or confidence > existing.confidence:
                existing.canonical_term = canonical_term
                existing.source = source
                existing.confidence = confidence
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            return existing

        mapping = SynonymMapping(
            canonical_term=canonical_term,
            synonym=synonym,
            source=source,
            confidence=confidence
        )
        self.db.add(mapping)
        await self.db.commit()
        await self.db.refresh(mapping)
        return mapping

    async def get_mapping(self, term: str) -> Optional[SynonymMapping]:
        """Get mapping for a term (if it is a synonym)."""
        stmt = select(SynonymMapping).where(SynonymMapping.synonym == term, SynonymMapping.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_canonical(self, term: str) -> str:
        """Get the canonical term for a given term (returns the term itself if no mapping exists)."""
        mapping = await self.get_mapping(term)
        if mapping:
            return mapping.canonical_term
        return term

    async def get_synonyms(self, canonical_term: str) -> List[str]:
        """Get all synonyms for a canonical term."""
        stmt = select(SynonymMapping.synonym).where(
            SynonymMapping.canonical_term == canonical_term,
            SynonymMapping.is_active == True
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_synonym(self, synonym: str) -> bool:
        """Delete a synonym mapping."""
        stmt = select(SynonymMapping).where(SynonymMapping.synonym == synonym)
        result = await self.db.execute(stmt)
        mapping = result.scalars().first()
        if mapping:
            await self.db.delete(mapping)
            await self.db.commit()
            return True
        return False

    async def list_mappings(self, skip: int = 0, limit: int = 100) -> List[SynonymMapping]:
        """List all synonym mappings."""
        stmt = select(SynonymMapping).where(SynonymMapping.is_active == True).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def bulk_add(self, mappings: List[Dict[str, str]]) -> int:
        """Bulk add synonyms. Each dict should have 'canonical' and 'synonym' keys."""
        count = 0
        for m in mappings:
            await self.add_synonym(m['canonical'], m['synonym'])
            count += 1
        return count
