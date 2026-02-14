import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import UploadFile
from app.services.input_processor import InputProcessor
from app.models.content import ContentItem

@pytest.mark.asyncio
async def test_process_text_input():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    processor = InputProcessor(mock_db)
    
    text = "Hello World"
    title = "Test Note"
    
    item = await processor.process_text_input(text, title, "user1")
    
    assert item.title == title
    assert item.content_text == text
    assert item.submitter_id == "user1"
    assert item.input_type == "text"
    
    assert mock_db.add.call_count >= 1
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called()

@pytest.mark.asyncio
async def test_process_url_input():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    processor = InputProcessor(mock_db)
    
    url = "http://example.com"
    mock_fetcher = AsyncMock()
    mock_fetcher.fetch.return_value = [{
        "title": "Example Domain",
        "url": url,
        "content": "Example Content",
        "summary": "Summary",
        "publish_time": None
    }]
    
    with patch("app.services.input_processor.get_fetcher", return_value=mock_fetcher):
        item = await processor.process_url_input(url, "user1")
        
        assert item.url == url
        assert item.content_text == "Example Content"
        assert item.input_type == "url"
        
        assert mock_db.add.call_count >= 1
        mock_db.commit.assert_called()

@pytest.mark.asyncio
async def test_process_file_input_text():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    processor = InputProcessor(mock_db)
    
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    file.read = AsyncMock(return_value=b"File Content")
    file.seek = AsyncMock()
    
    item = await processor.process_file_input(file, "user1")
    
    assert item.content_text == "File Content"
    assert item.input_type == "text"
    
    assert mock_db.add.call_count >= 1
    mock_db.commit.assert_called()
