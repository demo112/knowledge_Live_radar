import pytest
import uuid
from datetime import datetime, timedelta
from app.models.source import InformationSource
from app.models.crawl_job import CrawlJob

@pytest.mark.asyncio
async def test_get_source_history(client, db_session):
    # Create source
    source_id = uuid.uuid4()
    source = InformationSource(
        id=source_id,
        name="History Test Source",
        type="RSS",
        url="http://example.com/feed",
        status="ACTIVE",
        check_interval=3600
    )
    db_session.add(source)
    
    # Create jobs
    now = datetime.utcnow()
    
    for i in range(3):
        job = CrawlJob(
            id=uuid.uuid4(),
            source_id=source_id,
            status="COMPLETED",
            items_fetched=10 + i,
            items_new=i,
            created_at=now - timedelta(hours=i)
        )
        db_session.add(job)
        
    await db_session.commit()
    
    # Call API
    response = await client.get(f"/api/v1/sources/{source_id}/history")
        
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 3
    
    # Check ordering (descending by created_at)
    # i=0 is most recent
    assert data[0]["items_new"] == 0 
    assert data[1]["items_new"] == 1
    assert data[2]["items_new"] == 2
