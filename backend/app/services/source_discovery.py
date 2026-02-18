import uuid
from datetime import datetime
from typing import List, Optional
import logging
from duckduckgo_search import DDGS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.approval import Approval
from app.models.source import InformationSource
from app.models.pyramid import Pyramid, PyramidNode
from app.schemas.source import DiscoveredSource

logger = logging.getLogger(__name__)

class SourceDiscoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ddgs = DDGS()

    async def discover(self, pyramid_id: Optional[uuid.UUID] = None) -> int:
        """
        Execute source discovery task.
        1. Get keywords from pyramid nodes
        2. Search using DuckDuckGo
        3. Filter and validate results
        4. Create approval proposals
        
        Returns:
            Number of new proposals created
        """
        logger.info(f"Starting source discovery task. Pyramid ID: {pyramid_id}")
        
        # 1. Get keywords
        keywords = await self._get_keywords(pyramid_id)
        if not keywords:
            logger.info("No keywords found for discovery.")
            return 0
            
        logger.info(f"Generated {len(keywords)} keywords for search.")
        
        # 2. Search
        candidates = []
        for kw in keywords:
            try:
                # Search for blog RSS feeds
                # query format: "{keyword} 博客 RSS"
                query = f"{kw} 博客 RSS"
                logger.debug(f"Searching for: {query}")
                
                # Use synchronous DDGS in a way that doesn't block (ideally should be run in executor)
                # For simplicity in this iteration, we run it directly as it's a background task
                results = self.ddgs.text(query, region="cn-zh", max_results=5)
                
                if results:
                    for res in results:
                        candidates.append({
                            "url": res.get("href"),
                            "name": res.get("title"),
                            "description": res.get("body"),
                            "keyword": kw
                        })
            except Exception as e:
                logger.error(f"Error searching for {kw}: {e}")
                continue
                
        logger.info(f"Found {len(candidates)} candidate URLs.")
        
        # 3. Filter and Create Proposals
        created_count = 0
        for candidate in candidates:
            if not candidate.get("url"):
                continue
                
            # Basic validation
            url = candidate["url"]
            name = candidate["name"]
            
            # Check if exists in InformationSource
            exists_source = await self.db.execute(
                select(InformationSource).where(InformationSource.url == url)
            )
            if exists_source.scalar_one_or_none():
                continue
                
            # Check if exists in Approval (pending)
            exists_approval = await self.db.execute(
                select(Approval).where(
                    and_(
                        Approval.type == "create_source",
                        Approval.status == "pending",
                        # We need to check inside the JSON data, but for simplicity/performance 
                        # we might skip strict JSON check or check if we can extract URL from data
                        # Ideally Approval should have a unique constraint or we search by some field
                        # Here we iterate or use a more complex query if needed.
                        # For now, let's rely on application logic check.
                    )
                )
            )
            
            # Since URL is in JSON data, we fetch pending approvals and check in python
            # This is not efficient for large datasets but acceptable for "pending" list which should be small
            is_pending = False
            pending_approvals = exists_approval.scalars().all()
            for approval in pending_approvals:
                if approval.data and approval.data.get("url") == url:
                    is_pending = True
                    break
            
            if is_pending:
                continue
                
            # Create Approval
            try:
                new_approval = Approval(
                    id=uuid.uuid4(),
                    type="create_source",
                    status="pending",
                    data={
                        "url": url,
                        "name": name,
                        "description": candidate.get("description"),
                        "source_type": "RSS", # Default to RSS, user can change
                        "reason": f"与节点 '{candidate['keyword']}' 相关",
                        "tags": [candidate['keyword']]
                    },
                    generated_by="system",
                    reason=f"Auto-discovered based on keyword: {candidate['keyword']}",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.db.add(new_approval)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create approval for {url}: {e}")
                
        await self.db.commit()
        logger.info(f"Source discovery completed. Created {created_count} new proposals.")
        return created_count

    async def _get_keywords(self, pyramid_id: Optional[uuid.UUID]) -> List[str]:
        """
        Extract keywords from pyramid nodes.
        Prioritize leaf nodes and nodes with fewer contents.
        """
        query = select(PyramidNode)
        if pyramid_id:
            query = query.where(PyramidNode.pyramid_id == pyramid_id)
            
        # Get nodes that are active and not deleted
        query = query.where(PyramidNode.is_deleted == False)
        
        # Limit to avoid too many keywords
        # Strategy: Randomly pick 10 nodes or pick nodes with specific criteria
        # Here we pick latest updated nodes
        query = query.order_by(PyramidNode.updated_at.desc()).limit(10)
        
        result = await self.db.execute(query)
        nodes = result.scalars().all()
        
        keywords = set()
        for node in nodes:
            if node.name:
                keywords.add(node.name)
                
        return list(keywords)
