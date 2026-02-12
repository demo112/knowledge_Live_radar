
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_whitelist_lifecycle(client: AsyncClient):
    # 1. Add domain
    response = await client.post("/api/v1/whitelist/", json={
        "domain": "test-api.com",
        "credibility": 90,
        "reason": "API Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "test-api.com"
    domain_id = data["id"]

    # 2. Get list
    response = await client.get("/api/v1/whitelist/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["id"] == domain_id for item in data["items"])

    # 3. Check domain match (exact)
    response = await client.post("/api/v1/whitelist/check", json={
        "url": "https://test-api.com/some/path"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_whitelisted"] is True
    assert data["credibility"] == 90

    # 4. Remove domain
    response = await client.delete(f"/api/v1/whitelist/{domain_id}")
    assert response.status_code == 200

    # 5. Verify removal
    response = await client.get("/api/v1/whitelist/")
    data = response.json()
    assert not any(item["id"] == domain_id for item in data["items"])

@pytest.mark.asyncio
async def test_whitelist_wildcard(client: AsyncClient):
    # Add wildcard domain
    response = await client.post("/api/v1/whitelist/", json={
        "domain": "*.test-wildcard.com",
        "credibility": 75,
        "reason": "Wildcard Test"
    })
    assert response.status_code == 200
    domain_id = response.json()["id"]

    try:
        # Check subdomains
        subdomains = [
            "https://sub.test-wildcard.com",
            "https://a.b.test-wildcard.com",
            "https://test-wildcard.com" # Should match if implementation handles it, or maybe not strictly *.
        ]
        
        for url in subdomains:
            response = await client.post("/api/v1/whitelist/check", json={"url": url})
            data = response.json()
            # Note: My implementation checks suffix matching for *.
            # if domain.endswith(suffix) or domain == suffix
            assert data["is_whitelisted"] is True, f"Failed for {url}"
            assert data["credibility"] == 75

        # Check non-matching
        response = await client.post("/api/v1/whitelist/check", json={"url": "https://other-domain.com"})
        assert response.json()["is_whitelisted"] is False

    finally:
        # Cleanup
        await client.delete(f"/api/v1/whitelist/{domain_id}")
