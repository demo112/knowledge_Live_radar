import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import InformationSource
from app.models.content import ContentItem, ValidationResult
from datetime import datetime, timedelta
import uuid

@pytest.mark.asyncio
async def test_dashboard_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Create Source via API
    source_data = {
        "name": "Integration Test Source",
        "type": "RSS",
        "url": "https://example.com/rss",
        "check_interval": 60,
        "config": {"rss_url": "https://example.com/rss"},
        "template_id": "rss_standard"
    }
    response = await client.post("/api/v1/sources", json=source_data)
    assert response.status_code == 201
    source_id = response.json()["data"]["id"]

    # 2. Manually insert content and validation result
    # We use manual insertion because full crawl flow involves external calls/mocks which are complex for this test.
    # The goal is to verify dashboard aggregation logic.
    
    # Create Content Item
    content_id = uuid.uuid4()
    content = ContentItem(
        id=content_id,
        source_id=uuid.UUID(source_id),
        url="https://example.com/article/1",
        title="Test Article",
        status="PROCESSED",
        is_deleted=False
    )
    db_session.add(content)
    
    # Create Validation Result (Passed)
    validation_pass = ValidationResult(
        content_id=content_id,
        overall_score=85,
        hard_result={"passed": True},
        verified_at=datetime.now()
    )
    db_session.add(validation_pass)
    
    # Create another Content Item (Failed)
    content_id_fail = uuid.uuid4()
    content_fail = ContentItem(
        id=content_id_fail,
        source_id=uuid.UUID(source_id),
        url="https://example.com/article/2",
        title="Test Article 2",
        status="PROCESSED",
        is_deleted=False
    )
    db_session.add(content_fail)
    
    validation_fail = ValidationResult(
        content_id=content_id_fail,
        overall_score=40,
        hard_result={"passed": False},
        verified_at=datetime.now()
    )
    db_session.add(validation_fail)
    
    await db_session.commit()

    # 3. Check Dashboard Stats
    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["total_sources"] >= 1
    assert stats["total_contents"] >= 2
    # Pass rate: 1 passed / 2 total = 50%
    assert stats["validation_pass_rate"] == 50.0

    # 4. Check Dashboard Trend
    response = await client.get("/api/v1/dashboard/trend?days=7")
    assert response.status_code == 200
    trend = response.json()
    assert len(trend["trends"]) == 7
    
    # Verify today's data
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_data = next((t for t in trend["trends"] if t["date"] == today_str), None)
    
    assert today_data is not None
    assert today_data["total_validations"] >= 2
    assert today_data["pass_rate"] == 50.0
