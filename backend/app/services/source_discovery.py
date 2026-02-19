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
                yield DiscoveryEvent(event="log", data={"message": "未找到关键词。", "level": "warning"})
                yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.COMPLETED})
                return
            
            yield DiscoveryEvent(event="log", data={"message": f"已生成 {len(keywords)} 个关键词。", "level": "info"})
            yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.COMPLETED})
        except Exception as e:
            logger.error(f"Error getting keywords: {e}")
            yield DiscoveryEvent(event="error", data={"message": str(e)})
            return

        # 2. Search
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.RUNNING, "label": "执行搜索..."})
        candidates = []
        if not self.ddgs:
            yield DiscoveryEvent(event="error", data={"message": "搜索引擎初始化失败"})
            return

        total_keywords = len(keywords)
        for i, kw in enumerate(keywords):
            try:
                yield DiscoveryEvent(event="progress", data={"current": i+1, "total": total_keywords, "percentage": int((i+1)/total_keywords*100), "message": f"正在搜索: {kw}"})
                
                # query format: "{keyword} (site:zhihu.com OR site:juejin.cn OR site:csdn.net OR site:segmentfault.com OR inurl:rss)"
                # But simple search might be better: "{keyword} 博客" or "{keyword} 技术文章"
                # RSS specific search is often hard because many sites don't index rss xml well.
                # Let's try: "{keyword} 博客" to find blog homepages, then we can look for RSS links (future work).
                # For now, let's target tech blogs more specifically.
                query = f"{kw} (技术博客 OR 专栏 OR 官方文档)"
                logger.debug(f"Searching for: {query}")
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
                        
                        # Filter out common non-blog sites if needed
                        # e.g. baidu.com, google.com
                        if "baidu.com" in url or "google.com" in url:
                            continue

                        candidates.append({
                            "url": url,
                            "name": res.get("title") or "Unknown Title",
                            "description": res.get("body") or res.get("description") or "",
                            "keyword": kw
                        })
                        found_count += 1
                    yield DiscoveryEvent(event="log", data={"message": f"关键词 '{kw}' 找到 {found_count} 个结果", "level": "info"})
            except Exception as e:
                logger.error(f"Error searching for {kw}: {e}")
                yield DiscoveryEvent(event="log", data={"message": f"搜索 '{kw}' 失败: {str(e)}", "level": "error"})
                continue
        
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.COMPLETED})

        # 3. Filter
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.FILTER, "status": DiscoveryStatus.RUNNING, "label": "过滤结果..."})
        yield DiscoveryEvent(event="log", data={"message": f"正在过滤 {len(candidates)} 个候选结果...", "level": "info"})
        
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
            
        yield DiscoveryEvent(event="log", data={"message": f"跳过 {skipped_count} 个已存在或待审批的来源。", "level": "info"})
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
                    reason=f"基于关键词自动发现: {candidate['keyword']}",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.db.add(new_approval)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create approval: {e}")
                
        await self.db.commit()
        yield DiscoveryEvent(event="result", data={"count": created_count, "summary": f"创建了 {created_count} 个提案"})
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.PROPOSAL, "status": DiscoveryStatus.COMPLETED})
        yield DiscoveryEvent(event="finish", data={})

    async def _get_keywords(self, pyramid_id: Optional[uuid.UUID]) -> List[str]:
        """
        Extract keywords from pyramid nodes.
        Combine node name with parent name for better context.
        Prioritize leaf nodes and nodes with fewer contents.
        """
        # Eager load parent to construct context
        from sqlalchemy.orm import selectinload
        query = select(PyramidNode).options(selectinload(PyramidNode.parent))
        
        if pyramid_id:
            query = query.where(PyramidNode.pyramid_id == pyramid_id)
            
        # Get nodes that are active and not deleted
        query = query.where(PyramidNode.is_deleted == False)
        
        # Limit to avoid too many keywords
        # Strategy: Randomly pick 10 nodes or pick nodes with specific criteria
        # Here we pick nodes with fewer contents (prioritize under-explored nodes)
        query = query.order_by(PyramidNode.content_count.asc()).limit(10)
        
        result = await self.db.execute(query)
        nodes = result.scalars().all()
        
        keywords = set()
        for node in nodes:
            if not node.name: continue
            
            # Combine with parent name if exists for better context
            # e.g. "Tools" -> "Python Tools"
            kw = node.name
            if node.parent and node.parent.name:
                # Avoid redundancy if parent name is already part of node name
                if node.parent.name not in node.name:
                    kw = f"{node.parent.name} {node.name}"
            
            keywords.add(kw)
                
        return list(keywords)
