import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            
            # Use default embedding function (all-MiniLM-L6-v2)
            # This might require downloading the model on first run
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
            
            self.node_collection = self.client.get_or_create_collection(
                name="nodes",
                embedding_function=self.embedding_fn
            )
            
            self.content_collection = self.client.get_or_create_collection(
                name="contents",
                embedding_function=self.embedding_fn
            )
            logger.info(f"VectorService initialized. DB path: {settings.VECTOR_DB_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorService: {e}")
            raise e

    async def upsert_node_vector(self, node_id: UUID, name: str, description: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Upsert a node vector. Text = name + description.
        """
        try:
            text = f"{name}"
            if description:
                text += f": {description}"
            
            meta = metadata or {}
            meta["type"] = "node"
            meta["name"] = name
            
            self.node_collection.upsert(
                ids=[str(node_id)],
                documents=[text],
                metadatas=[meta]
            )
            logger.debug(f"Upserted node vector: {node_id}")
        except Exception as e:
            logger.error(f"Error upserting node vector {node_id}: {e}")
            # Non-blocking error for vector operations
            pass

    async def upsert_content_vector(self, content_id: UUID, title: str, summary: Optional[str] = None, concepts: Optional[List[str]] = None, metadata: Optional[Dict] = None):
        """
        Upsert a content vector. Text = title + summary + concepts.
        """
        try:
            text = f"{title}"
            if summary:
                text += f"\nSummary: {summary}"
            if concepts:
                text += f"\nConcepts: {', '.join(concepts)}"
            
            meta = metadata or {}
            meta["type"] = "content"
            meta["title"] = title
            
            self.content_collection.upsert(
                ids=[str(content_id)],
                documents=[text],
                metadatas=[meta]
            )
            logger.debug(f"Upserted content vector: {content_id}")
        except Exception as e:
            logger.error(f"Error upserting content vector {content_id}: {e}")
            pass

    async def search_similar_nodes(self, query_text: str, limit: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar nodes.
        """
        try:
            results = self.node_collection.query(
                query_texts=[query_text],
                n_results=limit
            )
            
            # Results structure: {'ids': [['id1', 'id2']], 'distances': [[0.1, 0.2]], ...}
            # Note: ChromaDB returns distances (lower is better for L2, but here we might be using cosine similarity depending on implementation details)
            # Default distance is L2. 
            # To normalize or interpret, we simply return what we get for now.
            # If using cosine, distance = 1 - similarity.
            
            parsed_results = []
            if results["ids"] and results["distances"]:
                ids = results["ids"][0]
                distances = results["distances"][0]
                metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)
                
                for i, node_id in enumerate(ids):
                    dist = distances[i]
                    # Simple conversion for L2 distance to "score" (heuristic)
                    # For cosine distance, score = 1 - distance
                    # Let's assume cosine-like behavior or just raw distance for now.
                    # If we want explicit score, we need to know the distance metric.
                    # Default sentence-transformers uses cosine similarity, but chromadb defaults to L2?
                    # Let's assume score = 1 / (1 + distance) for L2 or 1 - distance for cosine.
                    # We will return distance and let caller decide.
                    
                    parsed_results.append({
                        "id": UUID(node_id),
                        "distance": dist,
                        "metadata": metadatas[i]
                    })
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Error searching similar nodes: {e}")
            return []

    async def delete_node_vector(self, node_id: UUID):
        try:
            self.node_collection.delete(ids=[str(node_id)])
        except Exception as e:
            logger.error(f"Error deleting node vector {node_id}: {e}")

    async def delete_content_vector(self, content_id: UUID):
        try:
            self.content_collection.delete(ids=[str(content_id)])
        except Exception as e:
            logger.error(f"Error deleting content vector {content_id}: {e}")
