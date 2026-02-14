import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from app.services.input_parser import InputParser

@pytest.mark.asyncio
async def test_parse_image_ocr_flow():
    # Mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.png"
    mock_file.content_type = "image/png"
    mock_file.read = AsyncMock(return_value=b"fake_image_content")
    mock_file.seek = AsyncMock()

    # Mock AIService
    with patch("app.services.input_parser.AIService") as MockAIService:
        mock_ai_instance = MockAIService.return_value
        mock_ai_instance.client = True # Simulate enabled
        mock_ai_instance.chat_completion = AsyncMock(return_value="Extracted Text")

        result = await InputParser.parse_image(mock_file)

        assert result == "Extracted Text"
        
        # Verify call arguments
        mock_ai_instance.chat_completion.assert_called_once()
        call_args = mock_ai_instance.chat_completion.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["role"] == "user"
        content = call_args[0]["content"]
        assert len(content) == 2
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image_url"
        assert "data:image/png;base64," in content[1]["image_url"]["url"]

@pytest.mark.asyncio
async def test_parse_image_ocr_disabled():
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.jpg"
    mock_file.read = AsyncMock(return_value=b"content")
    mock_file.seek = AsyncMock()

    with patch("app.services.input_parser.AIService") as MockAIService:
        mock_ai_instance = MockAIService.return_value
        mock_ai_instance.client = None # Simulate disabled

        result = await InputParser.parse_image(mock_file)

        assert "OCR Unavailable" in result
