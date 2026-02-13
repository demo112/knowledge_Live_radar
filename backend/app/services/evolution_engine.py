from typing import List, Optional
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.vector_service import VectorService
from app.services.node_service import NodeService
from app.models.content import ContentItem
from app.models.pyramid import PyramidNode
from app.config import settings

logger = logging.getLogger(__name__)

class EvolutionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorService()
        self.node_service = NodeService(db)
        
        # Threshold for auto-classification
        # Distance is typically L2. Lower is better.
        # But we need to calibrate. For cosine similarity (1-dist), high is better.
        # Let's assume we use a distance threshold. If distance < threshold, match.
        # ChromaDB default is L2.
        # Let's use a conservative threshold or config.
        # For now, let's assume threshold 0.8 means "similarity score > 0.8" or "distance < 0.2" (if normalized).
        # To be safe, let's assume the VectorService returns raw distance, and we need to interpret it.
        # If we use cosine similarity in ChromaDB, it returns distance = 1 - cosine_similarity.
        # So threshold 0.8 (similarity) -> distance < 0.2.
        self.auto_classify_threshold = 0.5 # Default distance threshold (heuristic)

    async def auto_classify_content(self, content_item: ContentItem) -> int:
        """
        Automatically classify content into pyramid nodes.
        Returns number of linked nodes.
        """
        try:
            # 1. Upsert content vector first (ensure it's in vector DB)
            await self.vector_service.upsert_content_vector(
                content_id=content_item.id,
                title=content_item.title,
                summary=content_item.summary,
                concepts=content_item.concepts
            )
            
            # 2. Build query text
            query_text = content_item.title
            if content_item.summary:
                query_text += f"\n{content_item.summary}"
            if content_item.concepts:
                query_text += f"\n{', '.join(content_item.concepts)}"
                
            # 3. Search similar nodes
            similar_nodes = await self.vector_service.search_similar_nodes(
                query_text=query_text,
                limit=3 # Top 3 candidates
            )
            
            linked_count = 0
            for result in similar_nodes:
                node_id = result["id"]
                distance = result["distance"]
                
                # Check threshold
                # Assuming distance is L2 or Cosine Distance. Lower is better.
                # If distance < threshold, we link.
                if distance < self.auto_classify_threshold:
                    confidence = 1.0 - distance # Rough confidence estimate
                    if confidence < 0: confidence = 0.1
                    
                    logger.info(f"Auto-linking content {content_item.id} to node {node_id} (dist={distance:.4f})")
                    
                    await self.node_service.link_content(
                        node_id=node_id,
                        content_id=content_item.id,
                        source="ai_auto",
                        confidence=confidence
                    )
                    linked_count += 1
            
            return linked_count
            
        except Exception as e:
            logger.error(f"Error in auto_classify_content: {e}")
            return 0

    async def discover_clusters(self, pyramid_id: UUID):
        """
        Analyze unclassified content to discover new topic clusters.
        If a cluster of unlinked content shares similar concepts/tags,
        suggest creating a new node for them.
        """
        from app.models.content import ContentNodeRelation
        from app.models.approval import Approval
        from sqlalchemy import select, func
        from collections import Counter

        try:
            # 1. Find content items NOT linked to any node in this pyramid
            linked_ids_subq = (
                select(ContentNodeRelation.content_id)
                .join(PyramidNode, PyramidNode.id == ContentNodeRelation.node_id)
                .where(PyramidNode.pyramid_id == pyramid_id)
                .subquery()
            )
            result = await self.db.execute(
                select(ContentItem)
                .where(ContentItem.id.notin_(select(linked_ids_subq.c.content_id)))
                .where(ContentItem.tags.isnot(None))
                .order_by(ContentItem.created_at.desc())
                .limit(200)
            )
            unlinked = result.scalars().all()

            if len(unlinked) < 3:
                logger.info(f"Not enough unlinked content ({len(unlinked)}) for cluster discovery")
                return

            # 2. Count tag frequency across unlinked content
            tag_counter: Counter = Counter()
            tag_to_content: dict[str, list] = {}
            for item in unlinked:
                if not item.tags or not isinstance(item.tags, list):
                    continue
                for tag in item.tags:
                    if isinstance(tag, str) and len(tag) > 1:
                        tag_counter[tag] += 1
                        tag_to_content.setdefault(tag, []).append(item.id)

            # 3. Find clusters: tags appearing 3+ times in unlinked content
            cluster_threshold = 3
            clusters = [
                (tag, count, tag_to_content[tag])
                for tag, count in tag_counter.most_common(10)
                if count >= cluster_threshold
            ]

            if not clusters:
                logger.info("No significant clusters found in unlinked content")
                return

            # 4. For each cluster, check if a similar node already exists
            for tag, count, content_ids in clusters:
                similar_nodes = await self.vector_service.search_similar_nodes(tag, limit=1)
                if similar_nodes and similar_nodes[0]["distance"] < 0.3:
                    # Close match exists — suggest linking instead of creating
                    logger.info(f"Cluster '{tag}' matches existing node, skipping")
                    continue

                # 5. Generate proposal to create a new node
                # Find the best parent node via vector search
                parent_candidates = await self.vector_service.search_similar_nodes(tag, limit=1)
                parent_id = str(parent_candidates[0]["id"]) if parent_candidates else None

                proposal = Approval(
                    type="create_node",
                    status="pending",
                    generated_by="ai",
                    confidence_score=min(0.5 + count * 0.05, 0.95),
                    reason=f"Discovered topic cluster '{tag}' with {count} unlinked content items",
                    data={
                        "pyramid_id": str(pyramid_id),
                        "parent_id": parent_id,
                        "name": tag,
                        "description": f"Auto-discovered cluster: {count} content items about '{tag}'",
                        "content_ids": [str(cid) for cid in content_ids[:20]],
                    },
                )
                self.db.add(proposal)
                logger.info(f"Created cluster proposal: '{tag}' ({count} items)")

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error in discover_clusters: {e}")
            await self.db.rollback()
