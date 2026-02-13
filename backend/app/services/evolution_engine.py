from typing import List, Optional
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vector_service import VectorService
from app.services.node_service import NodeService
from app.models.content import ContentItem
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
        (Placeholder for future implementation)
        """
        pass
