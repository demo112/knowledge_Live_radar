import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import json
from urllib.parse import urlparse

from duckduckgo_search import DDGS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.approval import Approval
from app.models.source import InformationSource
from app.models.pyramid import Pyramid, PyramidNode
from app.schemas.source import DiscoveredSource, DiscoveryEvent, DiscoveryStage, DiscoveryStatus
from app.core.ai.facade import AIFacade

logger = logging.getLogger(__name__)

class SourceDiscoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIFacade()
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
        if not pyramid_id:
            yield DiscoveryEvent(event="error", data={"message": "Pyramid ID is required for adaptive discovery."})
            return

        if not self.ddgs:
            yield DiscoveryEvent(event="error", data={"message": "Search engine initialization failed."})
            return

        # 1. Extract Structure Snapshot
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.RUNNING, "label": "提取金字塔结构..."})
        try:
            snapshot = await self._get_structure_snapshot(pyramid_id)
            if not snapshot:
                yield DiscoveryEvent(event="error", data={"message": "Pyramid not found or empty."})
                return
            
            snapshot_json = json.dumps(snapshot, ensure_ascii=False, indent=2)
            yield DiscoveryEvent(event="log", data={"message": f"Structure snapshot extracted for '{snapshot['name']}'.", "level": "info"})
        except Exception as e:
            logger.error(f"Error extracting structure: {e}")
            yield DiscoveryEvent(event="error", data={"message": str(e)})
            return

        # 2. Generate Adaptive Queries
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.EXTRACT, "status": DiscoveryStatus.COMPLETED})
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.RUNNING, "label": "生成自适应查询..."})
        
        try:
            queries = await self.ai.generate_adaptive_queries(snapshot['name'], snapshot_json)
            if not queries:
                yield DiscoveryEvent(event="log", data={"message": "AI failed to generate queries, falling back to basic search.", "level": "warning"})
                queries = [{"query": f"{snapshot['name']} documentation blog", "intent": "fallback", "scope": "Macro"}]
            
            yield DiscoveryEvent(event="log", data={"message": f"Generated {len(queries)} adaptive queries.", "level": "info"})
        except Exception as e:
            logger.error(f"Error generating queries: {e}")
            yield DiscoveryEvent(event="error", data={"message": f"AI Query Generation Failed: {str(e)}"})
            return

        # 3. Execute Search
        candidates = []
        total_queries = len(queries)
        
        import asyncio
        
        for i, q_config in enumerate(queries):
            query_str = q_config.get("query")
            intent = q_config.get("intent", "unknown")
            scope = q_config.get("scope", "General")
            reason = q_config.get("reason", "")
            
            yield DiscoveryEvent(event="progress", data={
                "current": i+1, 
                "total": total_queries, 
                "percentage": int((i+1)/total_queries*100), 
                "message": f"[{scope}] {query_str}"
            })
            
            try:
                # Use synchronous DDGS in executor
                results = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: self.ddgs.text(query_str, region="cn-zh", max_results=8)
                )
                
                if results:
                    for res in results:
                        url = res.get("href") or res.get("url")
                        if not url: continue
                        
                        candidates.append({
                            "url": url,
                            "name": res.get("title") or "Unknown Title",
                            "description": res.get("body") or res.get("description") or "",
                            "query_context": {
                                "query": query_str,
                                "intent": intent,
                                "scope": scope,
                                "reason": reason
                            }
                        })
            except Exception as e:
                logger.error(f"Search failed for query '{query_str}': {e}")
                yield DiscoveryEvent(event="log", data={"message": f"Search failed for '{query_str}': {str(e)}", "level": "warning"})

        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.SEARCH, "status": DiscoveryStatus.COMPLETED})

        # 4. Filter & Create Proposals
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.FILTER, "status": DiscoveryStatus.RUNNING, "label": "过滤与去重..."})
        
        filtered_candidates = self._filter_results(candidates)
        yield DiscoveryEvent(event="log", data={"message": f"Filtered {len(candidates)} -> {len(filtered_candidates)} candidates.", "level": "info"})
        
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.PROPOSAL, "status": DiscoveryStatus.RUNNING, "label": "生成提案..."})
        
        created_count = 0
        for cand in filtered_candidates:
            # Check if source exists
            stmt = select(InformationSource).where(InformationSource.url == cand['url'])
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue
                
            # Check if approval exists
            stmt = select(Approval).where(
                and_(
                    Approval.data['url'].astext == cand['url'],
                    Approval.status == 'pending'
                )
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue

            # Create Approval
            ctx = cand['query_context']
            reason = f"[{ctx['scope']}] {ctx['intent']} (Reason: {ctx['reason']})"
            
            approval_data = {
                "name": cand['name'],
                "url": cand['url'],
                "type": "WEB", # Default to WEB, user can change
                "description": cand['description'],
                "source_context": reason
            }
            
            approval = Approval(
                type="create_source",
                data={**approval_data, "pyramid_id": str(pyramid_id)},
                status="pending",
                generated_by="ai",
                applicant_id="system",
                reason=reason
            )
            self.db.add(approval)
            created_count += 1
        
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to commit approvals: {e}")
            yield DiscoveryEvent(event="error", data={"message": "Failed to save proposals."})
            return

        yield DiscoveryEvent(event="result", data={"count": created_count, "message": f"Created {created_count} new source proposals."})
        yield DiscoveryEvent(event="stage_update", data={"stage": DiscoveryStage.FINISH, "status": DiscoveryStatus.COMPLETED})


    async def _get_structure_snapshot(self, pyramid_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Extract a simplified tree structure of the pyramid for AI context.
        """
        # Fetch pyramid
        stmt = select(Pyramid).where(Pyramid.id == pyramid_id)
        result = await self.db.execute(stmt)
        pyramid = result.scalar_one_or_none()
        if not pyramid:
            return None

        # Fetch all nodes
        stmt = select(PyramidNode).where(
            and_(
                PyramidNode.pyramid_id == pyramid_id,
                PyramidNode.is_deleted == False
            )
        ).order_by(PyramidNode.level, PyramidNode.sort_order)
        
        result = await self.db.execute(stmt)
        nodes = result.scalars().all()
        
        # Build tree
        node_map = {}
        roots = []
        
        for node in nodes:
            node_data = {
                "name": node.name,
                "description": node.description,
                "level": node.level,
                "children": []
            }
            # Only include ID if needed for internal logic, but for AI prompt name is enough
            
            node_map[node.id] = node_data
            
            if node.parent_id and node.parent_id in node_map:
                node_map[node.parent_id]["children"].append(node_data)
            elif node.level == 1:
                roots.append(node_data)
        
        # Prune tree for token limit (Simple heuristic: Depth limit 3)
        def prune(n, depth):
            if depth >= 3:
                n["children"] = [] # Cut off children at depth 3
                return
            for c in n["children"]:
                prune(c, depth + 1)
                
        for r in roots:
            prune(r, 1)

        return {
            "name": pyramid.name,
            "description": pyramid.description,
            "structure": roots
        }

    def _filter_results(self, candidates: List[Dict]) -> List[Dict]:
        """
        Filter and deduplicate search results.
        """
        seen_urls = set()
        filtered = []
        
        ignored_domains = [
            "baidu.com", "google.com", "bing.com", "sogou.com", 
            "so.com", "yahoo.com", "yandex.com",
            "facebook.com", "twitter.com", "instagram.com",
            "youtube.com", "bilibili.com", # Video sites might be good, but we focus on text for now unless specified
            "pinterest.com", "linkedin.com"
        ]
        
        for cand in candidates:
            url = cand['url']
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Rule 0: Skip if domain in ignored list
                if any(ignored in domain for ignored in ignored_domains):
                    continue
                
                # Rule 1: Deduplicate by domain (Keep only one result per domain? Or allow multiple if paths differ?)
                # Let's allow multiple if paths differ significantly, but exact URL duplicate check is must.
                if url in seen_urls:
                    continue
                
                # Rule 2: Prefer root or near-root paths for "Macro" scope
                # But allow deep paths for "Micro" scope.
                # So we don't aggressively filter by path depth anymore, relying on AI's query to find right pages.
                
                # Rule 3: Content-Type check (hard to do without fetching).
                # Assume search engine result is HTML.
                
                seen_urls.add(url)
                filtered.append(cand)
                
            except Exception:
                continue
                
        return filtered
