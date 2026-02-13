import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import select, or_, and_, desc, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.content import ContentItem, ContentNodeRelation
from app.models.pyramid import PyramidNode
from app.models.source import InformationSource
from app.models.content import ValidationResult # Implicitly used for score
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    keyword: str
    boolean_mode: bool = False
    node_ids: Optional[List[str]] = None
    include_children: bool = True
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    min_quality_score: Optional[int] = None
    validation_status: Optional[List[str]] = None
    sort_by: str = "relevance" # relevance/time/quality
    sort_order: str = "desc"

@dataclass
class SearchResult:
    total: int
    items: List[Dict[str, Any]]
    facets: Dict[str, Any]

class SearchService:
    def __init__(self):
        self.cache_service = cache_service
    
    async def search(self, query: SearchQuery, page: int = 1, size: int = 20) -> SearchResult:
        cache_key = f"search:{hash(str(query))}:{page}:{size}"
        cached = await self.cache_service.get(cache_key)
        if cached:
            return SearchResult(**cached)
            
        async with AsyncSessionLocal() as session:
            stmt = select(ContentItem)
            
            # Keywords
            if query.keyword:
                if query.boolean_mode:
                    filters = self._parse_boolean_query(query.keyword)
                    if filters is not None:
                        stmt = stmt.where(filters)
                    else:
                        # Fallback to simple search if parse fails
                        stmt = stmt.where(or_(
                            ContentItem.title.ilike(f"%{query.keyword}%"),
                            ContentItem.summary.ilike(f"%{query.keyword}%")
                        ))
                else:
                    stmt = stmt.where(or_(
                        ContentItem.title.ilike(f"%{query.keyword}%"),
                        ContentItem.summary.ilike(f"%{query.keyword}%")
                    ))
            
            # Node filtering
            if query.node_ids:
                if query.include_children:
                    # Need to find all children nodes first
                    # This is expensive without a closure table or recursive CTE
                    # Assuming materialized path 'path' in PyramidNode
                    node_ids_with_children = set(query.node_ids)
                    for node_id in query.node_ids:
                        # Find children
                        # Using subquery or simpler approach?
                        # For now, just direct match for simplicity or assume node_ids passed includes children if processed by frontend/API
                        # Implementing full tree traversal here might be complex.
                        # Let's rely on ContentNodeRelation
                        pass
                    
                    # Complex join needed.
                    stmt = stmt.join(ContentNodeRelation).where(ContentNodeRelation.node_id.in_(query.node_ids))
                else:
                    stmt = stmt.join(ContentNodeRelation).where(ContentNodeRelation.node_id.in_(query.node_ids))
            
            # Time range
            if query.time_start:
                stmt = stmt.where(ContentItem.created_at >= query.time_start)
            if query.time_end:
                stmt = stmt.where(ContentItem.created_at <= query.time_end)
                
            # Quality Score (Requires Join with ValidationResult)
            if query.min_quality_score is not None:
                stmt = stmt.join(ValidationResult).where(ValidationResult.overall_score >= query.min_quality_score)
                
            # Status
            if query.validation_status:
                stmt = stmt.where(ContentItem.status.in_(query.validation_status))
                
            # Sorting
            if query.sort_by == "time":
                order_col = ContentItem.created_at
            elif query.sort_by == "quality":
                # Ensure joined
                if query.min_quality_score is None: # Join if not already joined
                     stmt = stmt.join(ValidationResult, isouter=True)
                order_col = ValidationResult.overall_score
            else: # relevance
                # Simple relevance: title match ?
                # PG trgm supports relevance score, but keeping it simple for portable code
                order_col = ContentItem.created_at
                
            if query.sort_order == "asc":
                stmt = stmt.order_by(order_col.asc())
            else:
                stmt = stmt.order_by(order_col.desc())
                
            # Pagination
            # Total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt) or 0
            
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await session.execute(stmt)
            items = result.scalars().all()
            
            # Highlight
            item_dicts = []
            for item in items:
                d = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                if query.keyword:
                    d['title'] = self.highlight(d['title'], query.keyword)
                    if d.get('summary'):
                        d['summary'] = self.highlight(d['summary'], query.keyword)
                item_dicts.append(d)
                
            res = SearchResult(total=total, items=item_dicts, facets={})
            
            # Cache
            await self.cache_service.set(cache_key, res.__dict__, ttl=self.cache_service.SEARCH_CACHE_TTL)
            return res

    def highlight(self, text: str, keyword: str) -> str:
        if not text or not keyword:
            return text
        # Simple regex replace
        # For boolean query, this is hard. Just highlighting exact phrases or words.
        # Stripping boolean operators
        words = re.split(r'\s+(?:AND|OR|NOT)\s+|\s+', keyword)
        words = [w for w in words if w and w not in ('AND', 'OR', 'NOT')]
        
        for w in words:
            pattern = re.compile(re.escape(w), re.IGNORECASE)
            text = pattern.sub(lambda m: f"<em>{m.group(0)}</em>", text)
        return text

    def _parse_boolean_query(self, query: str):
        """
        Parse boolean query with AND, OR, NOT operators.
        Examples:
          "LLM AND agent" -> title/summary contains both
          "LLM OR agent" -> title/summary contains either
          "LLM NOT advertisement" -> contains LLM but not advertisement
        """
        try:
            query = query.strip()
            if not query:
                return None

            # Handle NOT first: "A NOT B" -> A and not B
            if " NOT " in query:
                parts = query.split(" NOT ", 1)
                include_part = parts[0].strip()
                exclude_part = parts[1].strip()
                
                include_filter = self._parse_boolean_query(include_part)
                exclude_filter = or_(
                    ContentItem.title.ilike(f"%{exclude_part}%"),
                    ContentItem.summary.ilike(f"%{exclude_part}%")
                )
                
                if include_filter is not None:
                    return and_(include_filter, ~exclude_filter)
                return ~exclude_filter

            # Handle OR: "A OR B"
            if " OR " in query:
                parts = [p.strip() for p in query.split(" OR ")]
                conditions = []
                for part in parts:
                    if part:
                        conditions.append(or_(
                            ContentItem.title.ilike(f"%{part}%"),
                            ContentItem.summary.ilike(f"%{part}%")
                        ))
                return or_(*conditions) if conditions else None

            # Handle AND: "A AND B"
            if " AND " in query:
                parts = [p.strip() for p in query.split(" AND ")]
                conditions = []
                for part in parts:
                    if part:
                        conditions.append(or_(
                            ContentItem.title.ilike(f"%{part}%"),
                            ContentItem.summary.ilike(f"%{part}%")
                        ))
                return and_(*conditions) if conditions else None

            # No operator — treat as simple keyword
            return or_(
                ContentItem.title.ilike(f"%{query}%"),
                ContentItem.summary.ilike(f"%{query}%")
            )
        except Exception as e:
            logger.error(f"Failed to parse boolean query '{query}': {e}")
            return None

    async def suggest(self, prefix: str, limit: int = 5) -> List[str]:
        # Suggest from history or existing titles
        async with AsyncSessionLocal() as session:
            stmt = select(ContentItem.title).where(ContentItem.title.ilike(f"{prefix}%")).limit(limit)
            res = await session.execute(stmt)
            return list(res.scalars().all())

search_service = SearchService()
