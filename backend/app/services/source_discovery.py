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
        try:
            self.ddgs = DDGS()
        except Exception as e:
            logger.error(f"Failed to initialize DDGS: {e}")
            self.ddgs = None

    async def discover(self, pyramid_id: Optional[uuid.UUID] = None) -> int:
        """
        Execute source discovery task (Synchronous wrapper).
        """
        count = 0
        async for event in self.discover_stream(pyramid_id):
            if event.event == "result":
                count = event.data.get("count", 0)
        return count

    async def discover_stream(self, pyramid_id: Optional[uuid.UUID] = None):
        """
        Execute source discovery task with streaming events.
        Yields DiscoveryEvent.
        """
        from app.schemas.source import DiscoveryEvent, DiscoveryStage, DiscoveryStatus
        
        # 1. Extract Keywords
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.RUNNING, "label": "提取关键词..."})
        try:
            keywords = await self._get_keywords(pyramid_id)
            if not keywords:
                yield DiscoveryEvent(event="log", data={"message": "No keywords found.", "level": "warning"})
                yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.COMPLETED})
                return
            
            yield DiscoveryEvent(event="log", data={"message": f"Generated {len(keywords)} keywords.", "level": "info"})
            yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.COMPLETED})
        except Exception as e:
            logger.error(f"Error getting keywords: {e}")
            yield DiscoveryEvent(event="error", data={"message": str(e)})
            return

        # 2. Search
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.RUNNING, "label": "执行搜索..."})
        candidates = []
        if not self.ddgs:
            yield DiscoveryEvent(event="error", data={"message": "Search engine not initialized"})
            return

        total_keywords = len(keywords)
        for i, kw in enumerate(keywords):
            try:
                yield DiscoveryEvent(event="progress", data={"current": i+1, "total": total_keywords, "percentage": int((i+1)/total_keywords*100), "message": f"Searching: {kw}"})
                
                query = f"{kw} 博客 RSS"
                import asyncio
                # Use synchronous DDGS in executor
                results = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: self.ddgs.text(query, region="cn-zh", max_results=5)
                )
                
                if results:
                    found_count = 0
                    for res in results:
                        url = res.get("href") or res.get("url")
                        if not url: continue
                        candidates.append({
                            "url": url,
                            "name": res.get("title") or "Unknown Title",
                            "description": res.get("body") or res.get("description") or "",
                            "keyword": kw
                        })
                        found_count += 1
                    yield DiscoveryEvent(event="log", data={"message": f"Found {found_count} results for '{kw}'", "level": "info"})
            except Exception as e:
                logger.error(f"Error searching for {kw}: {e}")
                yield DiscoveryEvent(event="log", data={"message": f"Error searching '{kw}': {str(e)}", "level": "error"})
                continue
        
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.COMPLETED})

        # 3. Filter
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.FILTER, "status": DiscoveryStatus.RUNNING, "label": "过滤结果..."})
        yield DiscoveryEvent(event="log", data={"message": f"Filtering {len(candidates)} candidates...", "level": "info"})
        
        valid_candidates = []
        skipped_count = 0
        for candidate in candidates:
            if not candidate.get("url"): continue
            
            # Check exist
            url = candidate["url"]
            exists_source = await self.db.execute(select(InformationSource).where(InformationSource.url == url))
            if exists_source.scalar_one_or_none():
                skipped_count += 1
                continue
                
            # Check pending
            exists_approval = await self.db.execute(select(Approval).where(and_(Approval.type == "create_source", Approval.status == "pending")))
            is_pending = False
            for approval in exists_approval.scalars().all():
                if approval.data and approval.data.get("url") == url:
                    is_pending = True
                    break
            if is_pending:
                skipped_count += 1
                continue
            
            valid_candidates.append(candidate)
            
        yield DiscoveryEvent(event="log", data={"message": f"Skipped {skipped_count} existing/pending sources.", "level": "info"})
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.FILTER, "status": DiscoveryStatus.COMPLETED})

        # 4. Proposal
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.PROPOSAL, "status": DiscoveryStatus.RUNNING, "label": "生成提案..."})
        created_count = 0
        for candidate in valid_candidates:
            try:
                new_approval = Approval(
                    id=uuid.uuid4(),
                    type="create_source",
                    status="pending",
                    data={
                        "url": candidate["url"],
                        "name": candidate["name"],
                        "description": candidate.get("description"),
                        "source_type": "RSS",
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
                logger.error(f"Failed to create approval: {e}")
                
        await self.db.commit()
        yield DiscoveryEvent(event="result", data={"count": created_count, "summary": f"Created {created_count} proposals"})
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.PROPOSAL, "status": DiscoveryStatus.COMPLETED})
        yield DiscoveryEvent(event="finish", data={})

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
