from typing import List, Optional
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.vector_service import VectorService
from app.services.knowledge_service import KnowledgeService
from app.models.content import ContentItem
from app.models.pyramid import PyramidNode
from app.core.ai.facade import ai_facade

logger = logging.getLogger(__name__)

class EvolutionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorService()
        self.knowledge_service = KnowledgeService(db)
        
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
        Automatically classify content into knowledge nodes (using AI cognitive models).
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
                
            # 3. Search similar knowledge nodes
            similar_nodes = await self.vector_service.search_similar_nodes(
                query_text=query_text,
                limit=3, # Top 3 candidates
                node_type="knowledge_node" # Filter for new KnowledgeNodes
            )
            
            linked_count = 0
            for result in similar_nodes:
                node_id_val = result["id"]
                # Ensure node_id is UUID
                if isinstance(node_id_val, str):
                    node_id = UUID(node_id_val)
                else:
                    node_id = node_id_val
                    
                distance = result["distance"]
                
                # Check threshold
                # Assuming distance is L2 or Cosine Distance. Lower is better.
                if distance < self.auto_classify_threshold:
                    confidence = 1.0 - distance # Rough confidence estimate
                    if confidence < 0: confidence = 0.1
                    
                    logger.info(f"Auto-linking content {content_item.id} to KnowledgeNode {node_id} (dist={distance:.4f})")
                    
                    # Use KnowledgeService to link
                    await self.knowledge_service.link_content(
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

    async def evolve_node_model(self, node_id: UUID) -> bool:
        """
        Evolve a KnowledgeNode's cognitive model based on recently linked content.
        Triggered when content count reaches a threshold or periodically.
        """
        try:
            node = await self.knowledge_service.get_node(node_id)
            if not node or not node.ai_model:
                logger.warning(f"Node {node_id} not found or has no AI model")
                return False

            # Get recently linked content (e.g., last 5 items)
            # We need to query ContentKnowledgeRelation
            from app.models.content import ContentKnowledgeRelation
            stmt = (
                select(ContentItem)
                .join(ContentKnowledgeRelation)
                .where(ContentKnowledgeRelation.node_id == node_id)
                .order_by(ContentKnowledgeRelation.created_at.desc())
                .limit(5)
            )
            result = await self.db.execute(stmt)
            recent_content = result.scalars().all()

            if not recent_content:
                logger.info(f"No content linked to node {node_id} to evolve model")
                # Debug print
                print(f"DEBUG: No content linked to node {node_id}")
                return False

            # Convert to dict for AI processing
            content_data = [
                {
                    "title": item.title,
                    "summary": item.summary or "",
                    "concepts": item.concepts or []
                }
                for item in recent_content
            ]

            # Evolve model via AI Facade
            logger.info(f"Evolving cognitive model for node {node.name} with {len(content_data)} items")
            new_model = await ai_facade.evolve_cognitive_model(node.ai_model, content_data)
            
            # Update node
            if new_model:
                await self.knowledge_service.update_node(node_id, ai_model=new_model)
                logger.info(f"Successfully evolved model for node {node.name}")
                return True
            
            return False

        except Exception as e:
            logger.error(f"Error in evolve_node_model: {e}")
            return False


