import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.ai.client import AIClient

@pytest.fixture
def mock_cloud_client():
    mock = AsyncMock()
    # Mock audio.transcriptions.create
    mock.audio = MagicMock() # .audio is usually a property accessing a resource
    mock.audio.transcriptions = MagicMock()
    mock.audio.transcriptions.create = AsyncMock(return_value=MagicMock(text="Hello world"))
    return mock

@pytest.fixture
def ai_client(mock_cloud_client):
    with patch("app.core.ai.client.configuration_service") as mock_config:
        # Mock configuration to return cloud enabled
        def config_get(key, default=None):
            if key == "ai.enabled": return True
            if key == "ai.api_key": return "test-key"
            if key == "ai.base_url": return "https://api.test.com"
            if key == "ai.model": return "test-model"
            return default
        
        mock_config.get.side_effect = config_get
        
        # We need to prevent _initialize_clients from overwriting our mock with a real client
        # because the AsyncOpenAI patch in the context manager below only lasts for the client creation.
        # When audio_transcriptions calls _initialize_clients, it would create a real client if not patched.
        
        with patch("app.core.ai.client.AsyncOpenAI", return_value=mock_cloud_client):
            client = AIClient()
            client._cloud_client = mock_cloud_client
            # Mock _initialize_clients to do nothing
            client._initialize_clients = MagicMock() 
            return client

@pytest.mark.asyncio
async def test_audio_transcriptions_success(ai_client, mock_cloud_client):
    file_path = "/tmp/test.mp3"
    
    # Use io.BytesIO to pass OpenAI library type checks
    import io
    f = io.BytesIO(b"audio data")
    f.name = "test.mp3"
    
    # Patch open to return our file-like object
    # io.BytesIO is a context manager that returns itself on __enter__
    with patch("builtins.open", return_value=f):
        # Call the method
        result = await ai_client.audio_transcriptions(file_path, model="whisper-1")
        
        assert result == "Hello world"
        mock_cloud_client.audio.transcriptions.create.assert_called_once()
        call_args = mock_cloud_client.audio.transcriptions.create.call_args
        assert call_args.kwargs["model"] == "whisper-1"
        assert call_args.kwargs["file"] == f

@pytest.mark.asyncio
async def test_audio_transcriptions_no_cloud_client():
    # Setup client with no cloud
    with patch("app.core.ai.client.configuration_service") as mock_config:
        mock_config.get.return_value = False # Disable AI
        client = AIClient()
        client._cloud_client = None
        
        with pytest.raises(RuntimeError, match="Cloud AI not initialized"):
             await client.audio_transcriptions("/tmp/test.mp3")
