import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from app.models.knowledge import KnowledgeNode
from app.models.concept import Concept
from app.core.ai.facade import ai_facade

@pytest.mark.asyncio
async def test_generate_cognitive_model_api(client, db_session):
    # 1. Create a node
    node = KnowledgeNode(
        id=uuid4(),
        name="Test Node",
        description="A test node description"
    )
    db_session.add(node)
    
    # 2. Create a concept matching the name
    concept = Concept(
        id=uuid4(),
        name="Test Node",
        type="technology",
        description="A concept matching the node name"
    )
    db_session.add(concept)
    await db_session.commit()
    
    # 3. Mock AI Facade
    mock_model = {
        "definition": "Generated definition",
        "key_attributes": ["attr1"],
        "related_concepts": [],
        "misconceptions": [],
        "evolution_path": []
    }
    
    with patch.object(ai_facade, 'generate_cognitive_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_model
        
        # 4. Call API
        response = await client.post(f"/api/v1/knowledge/nodes/{node.id}/cognitive-model")
        
        # 5. Verify
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Check if ai_model is populated
        assert data["ai_model"] == mock_model
        
        # Check if concept was automatically linked
        assert data["concept_id"] == str(concept.id)
        
        # Verify AI call context included concept info
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args.kwargs
        assert call_kwargs["name"] == "Test Node"
        assert "Concept Type: technology" in call_kwargs["context"]
        assert "Concept Description: A concept matching the node name" in call_kwargs["context"]
