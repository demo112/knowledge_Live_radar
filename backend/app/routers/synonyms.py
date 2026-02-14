from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.database import get_db
from app.services.concept.synonym_manager import SynonymManager
from app.schemas.synonym import SynonymResponse, SynonymCreate, SynonymBulkCreate

router = APIRouter(prefix="/synonyms", tags=["synonyms"])

@router.get("", response_model=List[SynonymResponse])
async def list_synonyms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    manager = SynonymManager(db)
    return await manager.list_mappings(skip, limit)

@router.post("/", response_model=SynonymResponse, status_code=status.HTTP_201_CREATED)
async def create_synonym(
    synonym_data: SynonymCreate,
    db: AsyncSession = Depends(get_db)
):
    manager = SynonymManager(db)
    return await manager.add_synonym(
        canonical_term=synonym_data.canonical_term,
        synonym=synonym_data.synonym,
        source=synonym_data.source,
        confidence=synonym_data.confidence
    )

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_synonyms(
    bulk_data: SynonymBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    manager = SynonymManager(db)
    # Convert Pydantic models to dicts for bulk_add
    mappings = [
        {"canonical": item.canonical_term, "synonym": item.synonym} 
        for item in bulk_data.mappings
    ]
    count = await manager.bulk_add(mappings)
    return {"count": count, "message": f"Successfully added {count} synonyms"}

@router.delete("/{synonym}")
async def delete_synonym(
    synonym: str,
    db: AsyncSession = Depends(get_db)
):
    manager = SynonymManager(db)
    success = await manager.delete_synonym(synonym)
    if not success:
        raise HTTPException(status_code=404, detail="Synonym not found")
    return {"message": "Synonym deleted successfully"}

@router.get("/canonical/{term}")
async def get_canonical_term(
    term: str,
    db: AsyncSession = Depends(get_db)
):
    manager = SynonymManager(db)
    canonical = await manager.get_canonical(term)
    return {"term": term, "canonical": canonical}
