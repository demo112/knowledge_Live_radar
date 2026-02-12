from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends

from app.services.search import search_service, SearchQuery, SearchResult

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=SearchResult)
async def search(
    q: str = Query(..., min_length=1),
    boolean: bool = False,
    node_ids: Optional[List[str]] = Query(None),
    include_children: bool = True,
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
    min_quality_score: Optional[int] = None,
    validation_status: Optional[List[str]] = Query(None),
    sort_by: str = "relevance",
    sort_order: str = "desc",
    page: int = 1,
    size: int = 20
):
    query = SearchQuery(
        keyword=q,
        boolean_mode=boolean,
        node_ids=node_ids,
        include_children=include_children,
        time_start=time_start,
        time_end=time_end,
        min_quality_score=min_quality_score,
        validation_status=validation_status,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await search_service.search(query, page, size)

@router.get("/suggest", response_model=List[str])
async def suggest(
    q: str = Query(..., min_length=1),
    limit: int = 5
):
    return await search_service.suggest(q, limit)
