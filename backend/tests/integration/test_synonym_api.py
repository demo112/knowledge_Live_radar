import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_synonym_crud_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Create a synonym
    create_data = {
        "canonical_term": "Artificial Intelligence",
        "synonym": "AI",
        "source": "manual",
        "confidence": 1.0
    }
    response = await client.post("/api/v1/synonyms/", json=create_data)
    assert response.status_code == 201
    data = response.json()
    assert data["canonical_term"] == "Artificial Intelligence"
    assert data["synonym"] == "AI"
    synonym_id = data["id"]

    # 2. List synonyms
    response = await client.get("/api/v1/synonyms/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    found = False
    for item in items:
        if item["synonym"] == "AI":
            found = True
            break
    assert found

    # 3. Get canonical term
    response = await client.get("/api/v1/synonyms/canonical/AI")
    assert response.status_code == 200
    data = response.json()
    assert data["canonical"] == "Artificial Intelligence"

    # 4. Get canonical term for unknown term (should return term itself)
    response = await client.get("/api/v1/synonyms/canonical/UnknownTerm")
    assert response.status_code == 200
    data = response.json()
    assert data["canonical"] == "UnknownTerm"

    # 5. Delete synonym
    response = await client.delete("/api/v1/synonyms/AI")
    assert response.status_code == 200
    
    # Verify deletion
    response = await client.get("/api/v1/synonyms/canonical/AI")
    data = response.json()
    # Should return "AI" because mapping is gone
    assert data["canonical"] == "AI"

@pytest.mark.asyncio
async def test_synonym_bulk_create(client: AsyncClient, db_session: AsyncSession):
    bulk_data = {
        "mappings": [
            {
                "canonical_term": "Machine Learning",
                "synonym": "ML",
                "confidence": 0.9
            },
            {
                "canonical_term": "Deep Learning",
                "synonym": "DL",
                "confidence": 0.9
            }
        ]
    }
    response = await client.post("/api/v1/synonyms/bulk", json=bulk_data)
    assert response.status_code == 201
    data = response.json()
    assert data["count"] == 2
    
    # Verify created
    response = await client.get("/api/v1/synonyms/canonical/ML")
    assert response.json()["canonical"] == "Machine Learning"
    
    response = await client.get("/api/v1/synonyms/canonical/DL")
    assert response.json()["canonical"] == "Deep Learning"
