import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from hypothesis import given, strategies as st, settings
from app.services.config.configuration_service import ConfigurationService

# Strategies for config values
valid_keys = st.sampled_from([
    "health.check_interval_hours",
    "hotspot.emerging_threshold", 
    "crawl.default_timeout_seconds"
])

@pytest.fixture
def config_service():
    # Reset singleton state
    ConfigurationService._instance = None
    ConfigurationService._config_cache = {}
    ConfigurationService._initialized = False
    
    with patch("app.services.config.configuration_service.AsyncSessionLocal"), \
         patch("builtins.open", new_callable=MagicMock), \
         patch("app.services.config.configuration_service.os.path.exists", return_value=False), \
         patch("app.services.config.configuration_service.asyncio.to_thread", side_effect=lambda f, *args: f(*args)):
        service = ConfigurationService()
        # Initialize with defaults to ensure keys exist for validation
        service._config_cache = service._get_defaults()
        return service

@pytest.mark.asyncio
@given(key=valid_keys, value=st.integers(min_value=0, max_value=1000))
@settings(max_examples=20)
async def test_property_config_set_get_consistency(key, value):
    """Property 22: Config hot update roundtrip consistency"""
    
    ConfigurationService._instance = None
    ConfigurationService._config_cache = {}
    ConfigurationService._initialized = False
    
    with patch("app.services.config.configuration_service.AsyncSessionLocal") as mock_db, \
         patch("builtins.open", new_callable=MagicMock), \
         patch("app.services.config.configuration_service.os.path.exists", return_value=False), \
         patch("app.services.config.configuration_service.asyncio.to_thread", side_effect=lambda f, *args: f(*args)):
         
        service = ConfigurationService()
        # Pre-fill cache with defaults so validation passes (type check)
        service._config_cache = service._get_defaults()
        
        # Mock commit
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        await service.set(key, value)
        assert service.get(key) == value

@pytest.mark.asyncio
async def test_api_key_masking(config_service):
    """Property 1: API Key Masking Consistency"""
    # Test sensitive key masking
    key = "ai.api_key"
    value = "sk-1234567890abcdef"
    config_service._config_cache[key] = value
    masked = config_service.get_masked(key)
    assert masked == "sk-1***cdef"
    assert "***" in masked
    
    # Test short sensitive key masking (should not mask if <= 8 chars)
    short_value = "12345678"
    config_service._config_cache[key] = short_value
    # Assuming implementation masks if > 8 chars
    assert config_service.get_masked(key) == short_value
    
    # Test non-sensitive key not masking
    config_service._config_cache["other.key"] = "very_long_value_that_is_not_sensitive"
    # Assuming "other.key" is not in sensitive list and doesn't contain "password"/"secret"
    assert config_service.get_masked("other.key") == "very_long_value_that_is_not_sensitive"

@pytest.mark.asyncio
async def test_masked_value_update_rejection(config_service):
    """Property 2: Masked Value Update Rejection"""
    key = "ai.api_key"
    original_value = "sk-original-key-12345"
    config_service._config_cache[key] = original_value
    
    # Try to set the masked value back
    masked_value = "sk-o***2345" # Simulating a masked input
    
    # Mock save and history
    with patch.object(config_service, '_save_to_file', new_callable=AsyncMock), \
         patch.object(config_service, '_record_history', new_callable=AsyncMock) as mock_history:
        
        await config_service.set(key, masked_value)
        
        # Verify value didn't change 
        assert config_service.get(key) == original_value
        
        # Verify history was NOT recorded (because update was skipped)
        mock_history.assert_not_called()

@pytest.mark.asyncio
async def test_config_validation_rules(config_service):
    """Property 3: Configuration Validation Rules"""
    
    # Test valid URL
    config_service._validate("ai.base_url", "https://api.example.com/v1")
    
    # Test invalid URL
    with pytest.raises(ValueError, match="valid URL"):
        config_service._validate("ai.base_url", "not-a-url")
        
    # Test valid temperature
    config_service._validate("ai.temperature", 0.7)
    config_service._validate("ai.temperature", 0.0)
    config_service._validate("ai.temperature", 2.0)
    
    # Test invalid temperature
    with pytest.raises(ValueError, match="between 0.0 and 2.0"):
        config_service._validate("ai.temperature", -0.1)
    with pytest.raises(ValueError, match="between 0.0 and 2.0"):
        config_service._validate("ai.temperature", 2.1)
        
    # Test valid max_retries
    config_service._validate("ai.max_retries", 3)
    
    # Test invalid max_retries
    with pytest.raises(ValueError, match="positive integer"):
        config_service._validate("ai.max_retries", 0)
    with pytest.raises(ValueError, match="positive integer"):
        config_service._validate("ai.max_retries", -1)

@pytest.mark.asyncio
async def test_config_history_recording(config_service):
    """Property 4: Configuration Change History Recording"""
    key = "ai.temperature"
    old_val = 0.3
    new_val = 0.8
    config_service._config_cache[key] = old_val
    
    with patch.object(config_service, '_save_to_file', new_callable=AsyncMock), \
         patch.object(config_service, '_record_history', new_callable=AsyncMock) as mock_history:
         
        await config_service.set(key, new_val, user_id="tester")
        
        mock_history.assert_called_once_with(key, old_val, new_val, "tester")
        assert config_service.get(key) == new_val
