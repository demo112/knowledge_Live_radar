import pytest
import shutil
import tempfile
import os
from unittest.mock import patch
from app.config import settings
from app.services.input_processor import InputProcessor
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeNodeCreate
from app.services.evolution_engine import EvolutionEngine
from app.models.content import ContentKnowledgeRelation
from sqlalchemy import select

# We need to ensure we use a fresh vector DB path for this test
@pytest.fixture
def temp_vector_db_path():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.mark.asyncio
async def test_e2e_real_vector_integration(db_session, temp_vector_db_path):
    """
    E2E Scenario with REAL ChromaDB (no mocks):
    Ingest content -> Classify (via Real ChromaDB) -> Link to Node.
    
    Uses DeterministicEmbeddingFunction (via conftest.py env var), so we rely on 
    exact text matching to ensure distance is 0.
    """
    
    # 1. Override settings.VECTOR_DB_PATH
    # We need to patch it where it is used or update the singleton if possible.
    # Since VectorService reads settings.VECTOR_DB_PATH in __init__, 
    # we just need to patch it before initializing EvolutionEngine (which initializes VectorService).
    
    with patch("app.config.settings.VECTOR_DB_PATH", temp_vector_db_path):
        
        # 2. Setup Services
        input_processor = InputProcessor(db_session)
        knowledge_service = KnowledgeService(db_session)
        
        # 3. Create a Node (Target)
        # Name it "ExactMatch" so we can match it easily with deterministic embeddings.
        # CRITICAL: Description must be None so that the vector text is exactly "ExactMatch".
        # If description exists, VectorService appends it, changing the hash.
        node = await knowledge_service.create_node(KnowledgeNodeCreate(
            name="ExactMatch", 
            description=None, 
            node_type="concept"
        ))
        
        # 4. Ingest Content
        # We set title to "ExactMatch" so the query vector matches the node vector exactly.
        # DeterministicEmbeddingFunction: hash("ExactMatch") == hash("ExactMatch") -> distance 0
        content = await input_processor.process_text_input(
            text="This content should match because the title is identical to node name.",
            title="ExactMatch"
        )
        
        # 5. Initialize EvolutionEngine
        # This will spin up VectorService with the temp path
        evolution_engine = EvolutionEngine(db_session)
        
        # Verify VectorService is using our temp path (indirectly via logs or trust the patch)
        # The key is that we are NOT mocking vector_service methods here.
        
        # 6. Trigger Auto Classification
        linked_count = await evolution_engine.auto_classify_content(content)
        
        # 7. Assertions
        assert linked_count == 1
        
        # Verify Linkage in DB
        stmt = select(ContentKnowledgeRelation).where(
             ContentKnowledgeRelation.node_id == node.id,
             ContentKnowledgeRelation.content_id == content.id
        )
        result = await db_session.execute(stmt)
        relation = result.scalar_one_or_none()
        
        assert relation is not None
        # Since distance should be 0 (exact match), confidence should be 1.0
        assert relation.confidence > 0.95
