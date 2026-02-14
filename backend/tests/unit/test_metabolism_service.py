import pytest
from datetime import datetime, timezone, timedelta
from app.services.metabolism_service import MetabolismService
from app.models.content import ContentItem
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_calculate_score():
    # Mock item
    item = ContentItem(
        created_at=datetime.now(timezone.utc),
        access_count=0,
        validation_result=None
    )
    service = MetabolismService(None)
    
    # Test 1: Fresh item, default quality
    score = service.calculate_score(item)
    assert 49.0 < score < 51.0  # Should be around 50

    # Test 2: Old item (180 days), decay factor ~0.36
    item.created_at = datetime.now(timezone.utc) - timedelta(days=180)
    score = service.calculate_score(item)
    # 50 * exp(-1) = 50 * 0.3678 = 18.39
    assert 18.0 < score < 19.0

    # Test 3: Popular item (100 views), boost ~1.46
    item.created_at = datetime.now(timezone.utc)
    item.access_count = 100
    score = service.calculate_score(item)
    # 50 * 1 * (1 + 0.1 * ln(101)) = 50 * (1 + 0.1 * 4.6) = 50 * 1.46 = 73
    assert 72.0 < score < 74.0

@pytest.mark.asyncio
async def test_process_metabolism_transitions():
    # Setup mock DB
    mock_db = AsyncMock()
    service = MetabolismService(mock_db)
    
    # Mock items
    now = datetime.now(timezone.utc)
    
    # Item 1: Active, low score, old -> Should become DEPRECATED
    # Score: 50 * exp(-60/180) = 50 * 0.716 = 35.8 < 40
    item1 = ContentItem(
        id="1",
        lifecycle_status="ACTIVE",
        created_at=now - timedelta(days=60),
        last_accessed_at=now,
        access_count=0,
        validation_result=None 
    )
    
    # Item 2: Deprecated, old, inactive -> Should become ARCHIVED
    item2 = ContentItem(
        id="2",
        lifecycle_status="DEPRECATED",
        created_at=now - timedelta(days=100),
        last_accessed_at=now - timedelta(days=40),
        access_count=0,
        validation_result=None
    )
    
    # Mock DB execute result
    mock_result = MagicMock()
    # First call returns items, second call returns empty list to stop loop
    mock_result.scalars.return_value.all.side_effect = [[item1, item2], []]
    mock_db.execute.return_value = mock_result
    
    stats = await service.process_metabolism()
    
    assert item1.lifecycle_status == "DEPRECATED"
    assert item2.lifecycle_status == "ARCHIVED"
    assert stats["to_deprecated"] == 1
    assert stats["to_archived"] == 1
