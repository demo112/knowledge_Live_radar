from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.services.knowledge_service import KnowledgeService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

class DiscoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.knowledge_service = KnowledgeService(db)
        self.vector_service = VectorService()

    async def discover_node_relations(self, node_id: UUID, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Discover potential relations for a given node based on vector similarity.
        Returns a list of potential relations (not saved to DB yet).
        """
        node = await self.knowledge_service.get_node(node_id)
        if not node:
            logger.warning(f"Node {node_id} not found for discovery")
            return []

        # 1. Get embedding for the node (or use its text to search)
        query_text = f"{node.name}"
        if node.description:
            query_text += f": {node.description}"
        
        # 2. Search similar nodes
        # Fetch more to filter out self and existing relations
        similar_nodes = await self.vector_service.search_similar_nodes(query_text, limit=limit + 10, node_type=None)
        
        discovered_relations = []
        
        # 3. Get existing relations to filter
        existing_relations = await self.knowledge_service.get_node_relations(node_id)
        existing_target_ids = set()
        for r in existing_relations:
            if r.source_node_id == node_id:
                existing_target_ids.add(r.target_node_id)
            else:
                existing_target_ids.add(r.source_node_id)
        
        existing_target_ids.add(node_id) # Exclude self
        
        for result in similar_nodes:
            try:
                target_id = UUID(result["id"])
            except ValueError:
                logger.warning(f"Invalid UUID returned from vector search: {result['id']}")
                continue
                
            if target_id in existing_target_ids:
                continue
                
            # VectorService returns 'distance'. 
            # Assuming L2 distance (lower is better), we convert to similarity.
            distance = result["distance"]
            similarity = 1 / (1 + distance)
            
            if similarity < threshold:
                continue
                
            discovered_relations.append({
                "source_node_id": node_id,
                "target_node_id": target_id,
                "relation_type": "related", # Default type
                "confidence": similarity,
                "reason": f"Vector similarity score: {similarity:.2f}"
            })
            
            if len(discovered_relations) >= limit:
                break
                
        return discovered_relations

    async def discover_content_clusters(self, batch_size: int = 50, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Discover potential clusters from unlinked content.
        Uses a simple connected components algorithm on the similarity graph.
        """
        from app.models.content import ContentItem, ContentKnowledgeRelation
        from sqlalchemy import select
        
        # 1. Fetch unlinked content IDs
        # We look for content that is NOT in ContentKnowledgeRelation
        subquery = select(ContentKnowledgeRelation.content_id)
        stmt = (
            select(ContentItem.id, ContentItem.title)
            .where(ContentItem.id.not_in(subquery))
            .limit(batch_size)
        )
        
        result = await self.db.execute(stmt)
        unlinked_content = result.all() # [(id, title), ...]
        
        if not unlinked_content:
            return []
            
        unlinked_ids = [row.id for row in unlinked_content]
        id_to_title = {row.id: row.title for row in unlinked_content}
        
        # 2. Get embeddings
        id_to_embedding = await self.vector_service.get_content_embeddings(unlinked_ids)
        
        if not id_to_embedding:
            return []
            
        # Filter unlinked_ids to only those we have embeddings for
        valid_ids = [uid for uid in unlinked_ids if str(uid) in id_to_embedding]
        
        if len(valid_ids) < 3: # Need at least 3 for a cluster
            return []

        # 3. Simple clustering (Connected Components)
        # O(N^2) pairwise comparison
        adj = {uid: set() for uid in valid_ids}
        
        for i in range(len(valid_ids)):
            for j in range(i + 1, len(valid_ids)):
                uid_i = valid_ids[i]
                uid_j = valid_ids[j]
                
                vec_i = id_to_embedding[str(uid_i)]
                vec_j = id_to_embedding[str(uid_j)]
                
                # Manual cosine similarity
                dot_product = sum(a*b for a,b in zip(vec_i, vec_j))
                norm_i = sum(a*a for a in vec_i) ** 0.5
                norm_j = sum(b*b for b in vec_j) ** 0.5
                
                if norm_i * norm_j == 0:
                    sim = 0
                else:
                    sim = dot_product / (norm_i * norm_j)
                    
                if sim >= similarity_threshold:
                    adj[uid_i].add(uid_j)
                    adj[uid_j].add(uid_i)
        
        # Find connected components
        visited = set()
        clusters = []
        
        for uid in valid_ids:
            if uid not in visited:
                component = []
                stack = [uid]
                visited.add(uid)
                while stack:
                    node = stack.pop()
                    component.append(node)
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)
                
                if len(component) >= 3: # Min cluster size
                    clusters.append(component)
        
        results = []
        for idx, comp in enumerate(clusters):
            titles = [id_to_title[cid] for cid in comp]
            results.append({
                "cluster_label": idx,
                "content_ids": comp,
                "titles": titles,
                "size": len(comp),
                "suggested_name": f"Cluster: {titles[0]}..."
            })
            
        return results
