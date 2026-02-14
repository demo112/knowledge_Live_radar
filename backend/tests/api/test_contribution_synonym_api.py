import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_synonym_api_flow(client: AsyncClient):
    # 1. Create Synonym
    response = await client.post(
        "/api/v1/synonyms/",
        json={
            "canonical_term": "AI",
            "synonym": "Artificial Intelligence",
            "source": "test",
            "confidence": 0.95
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["canonical_term"] == "AI"
    assert data["synonym"] == "Artificial Intelligence"
    
    # 2. Get Canonical
    response = await client.get("/api/v1/synonyms/canonical/Artificial Intelligence")
    assert response.status_code == 200
    assert response.json()["canonical"] == "AI"
    
    # 3. List Synonyms
    response = await client.get("/api/v1/synonyms/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    
    # 4. Delete Synonym
    response = await client.delete("/api/v1/synonyms/Artificial Intelligence")
    assert response.status_code == 200
    
    # Verify Deletion
    response = await client.get("/api/v1/synonyms/canonical/Artificial Intelligence")
    assert response.json()["canonical"] == "Artificial Intelligence"  # Should return self if no mapping

@pytest.mark.asyncio
async def test_contribution_api_flow(client: AsyncClient):
    # 1. Get Stats (should be empty or initial state)
    response = await client.get("/api/v1/contributions/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    
    # 2. List Contributions
    response = await client.get("/api/v1/contributions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Note: Creating contribution is done via input processing, which is tested separately.
    # We can try to simulate one if needed, but for now we just test read APIs.
