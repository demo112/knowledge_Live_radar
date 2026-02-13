import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.search.search_service import SearchService, SearchQuery, SearchResult

@pytest.fixture
def search_service():
    with patch("app.services.search.search_service.cache_service") as mock_cache:
        mock_cache.SEARCH_CACHE_TTL = 300
        service = SearchService()
        service.cache_service = mock_cache
        yield service

@pytest.mark.asyncio
async def test_search_cache_hit(search_service):
    query = SearchQuery(keyword="test")
    cached_data = {
        "total": 10,
        "items": [{"id": "1", "title": "Test"}],
        "facets": {}
    }
    search_service.cache_service.get = AsyncMock(return_value=cached_data)
    
    result = await search_service.search(query)
    
    assert isinstance(result, SearchResult)
    assert result.total == 10
    assert result.items[0]["title"] == "Test"

@pytest.mark.asyncio
async def test_search_cache_miss(search_service):
    query = SearchQuery(keyword="test")
    search_service.cache_service.get = AsyncMock(return_value=None)
    search_service.cache_service.set = AsyncMock()
    
    # Mock DB session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    # Mock Item
    mock_item = MagicMock()
    mock_item.id = "1"
    mock_item.title = "Test Item"
    mock_item.summary = "A summary with test keyword"
    mock_item.created_at = "2023-01-01"
    
    # Mock columns for serialization
    col_id = MagicMock()
    col_id.name = "id"
    col_title = MagicMock()
    col_title.name = "title"
    col_summary = MagicMock()
    col_summary.name = "summary"
    col_created = MagicMock()
    col_created.name = "created_at"
    
    mock_table = MagicMock()
    mock_table.columns = [col_id, col_title, col_summary, col_created]
    mock_item.configure_mock(__table__=mock_table)
    
    # Mock scalar (count)
    mock_session.scalar.return_value = 1
    
    # Mock execute (items)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_item]
    mock_session.execute.return_value = mock_result
    
    with patch("app.services.search.search_service.AsyncSessionLocal", return_value=mock_session):
        result = await search_service.search(query)
        
        assert result.total == 1
        assert len(result.items) == 1
        # The keyword is "test", title is "Test Item". 
        # highlight uses re.IGNORECASE, so "Test" becomes "<em>Test</em>"
        assert result.items[0]["title"] == "<em>Test</em> Item"
        
        # Verify cache set
        search_service.cache_service.set.assert_called_once()

