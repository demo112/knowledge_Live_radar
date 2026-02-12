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
        
        # Mock commit
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        await service.set(key, value)
        assert service.get(key) == value

@pytest.mark.asyncio
@given(key=valid_keys, value=st.integers(min_value=-100, max_value=-1))
@settings(max_examples=20)
async def test_property_config_rejects_negative(key, value):
    """Property 20: Config validation rejects invalid values"""
    ConfigurationService._instance = None
    ConfigurationService._config_cache = {}
    ConfigurationService._initialized = False
    
    with patch("app.services.config.configuration_service.AsyncSessionLocal"), \
         patch("builtins.open", new_callable=MagicMock), \
         patch("app.services.config.configuration_service.os.path.exists", return_value=False), \
         patch("app.services.config.configuration_service.asyncio.to_thread", side_effect=lambda f, *args: f(*args)):
         
        service = ConfigurationService()
        
        with pytest.raises(ValueError):
            await service.set(key, value)

@pytest.mark.asyncio
@given(key=valid_keys, value=st.integers(min_value=1, max_value=100))
@settings(max_examples=20)
async def test_property_config_history_integrity(key, value):
    """Property 21: Config change history is recorded"""
    ConfigurationService._instance = None
    ConfigurationService._config_cache = {}
    ConfigurationService._initialized = False
    
    with patch("app.services.config.configuration_service.AsyncSessionLocal") as mock_db, \
         patch("builtins.open", new_callable=MagicMock), \
         patch("app.services.config.configuration_service.os.path.exists", return_value=False), \
         patch("app.services.config.configuration_service.asyncio.to_thread", side_effect=lambda f, *args: f(*args)):
         
        service = ConfigurationService()
        mock_session = AsyncMock()
        mock_session.add = MagicMock() # add is sync
        mock_db.return_value.__aenter__.return_value = mock_session
        
        old_val = service.get(key)
        await service.set(key, value)
        
        # Check if history was added
        if old_val != value:
            assert mock_session.add.called
            args = mock_session.add.call_args[0]
            history_entry = args[0]
            assert history_entry.config_key == key
            assert history_entry.new_value == value
        else:
            assert not mock_session.add.called
