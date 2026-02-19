import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add backend path
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.services.source_discovery import SourceDiscoveryService

async def test_stream():
    # Mock DB
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Initialize service
    service = SourceDiscoveryService(mock_db)
    
    # Mock _get_keywords
    service._get_keywords = AsyncMock(return_value=["TestKeyword1", "TestKeyword2"])
    
    # Mock DDGS
    # Since ddgs.text is called in run_in_executor, we need to mock the instance method
    service.ddgs = MagicMock()
    service.ddgs.text.return_value = [
        {"href": "http://example.com/1", "title": "Test 1", "body": "Desc 1"},
        {"href": "http://example.com/2", "title": "Test 2", "body": "Desc 2"}
    ]

    print("Starting stream test...")
    try:
        async for event in service.discover_stream():
            print(f"Event: {event.event}, Data: {event.data}")
    except Exception as e:
        print(f"Error during stream: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream())
