import pytest
import asyncio
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_service import AIService

# Mock configuration_service to avoid side effects
@pytest.fixture(autouse=True)
def mock_config():
    with patch("app.services.ai_service.configuration_service") as mock:
        # Default behavior
        mock.get.return_value = None
        yield mock

@pytest.mark.asyncio
async def test_ai_service_initialization():
    """Basic test to verify initialization logic with mocks"""
    with patch("app.services.ai_service.configuration_service") as mock_config:
        mock_config.get.side_effect = lambda k: True if k == "ai.enabled" else "key"
        with patch("app.services.ai_service.AsyncOpenAI") as mock_openai:
            service = AIService()
            assert service.client is not None

# Property Tests

@given(
    enabled=st.booleans(),
    api_key=st.text(min_size=0, max_size=10),
    base_url=st.text(min_size=5, max_size=20)
)
@hypothesis_settings(max_examples=100)
def test_ai_service_dynamic_config_prop(enabled, api_key, base_url):
    """Property 6: Dynamic configuration reading"""
    
    async def run_test():
        with patch("app.services.ai_service.configuration_service") as mock_config:
            def get_side_effect(key):
                if key == "ai.enabled": return enabled
                if key == "ai.api_key": return api_key
                if key == "ai.base_url": return base_url
                return None
            mock_config.get.side_effect = get_side_effect
            
            with patch("app.services.ai_service.AsyncOpenAI") as mock_openai:
                service = AIService()
                
                # Force re-initialization logic check by accessing client
                # (AIService logic: client property calls _initialize_client)
                client = service.client
                
                if enabled and api_key:
                    assert client is not None
                    # Ensure AsyncOpenAI was called with correct args
                    mock_openai.assert_called()
                    call_args = mock_openai.call_args
                    assert call_args.kwargs['api_key'] == api_key
                    assert call_args.kwargs['base_url'] == base_url
                else:
                    assert client is None

    # Run async test
    asyncio.run(run_test())

@given(
    title=st.text(),
    content=st.text()
)
@hypothesis_settings(max_examples=100)
def test_ai_degradation_prop(title, content):
    """Property 5: AI disabled degradation behavior"""
    
    async def run_test():
        with patch("app.services.ai_service.configuration_service") as mock_config:
            # Simulate DISABLED state
            mock_config.get.side_effect = lambda k: False if k == "ai.enabled" else None
            
            with patch("app.services.ai_service.AsyncOpenAI"):
                service = AIService()
                
                # Verify client is None
                assert service.client is None
                
                # Test validate_content_soft
                res = await service.validate_content_soft(title, content)
                assert res["score"] == 100
                assert res["reason"] == "Skipped (AI disabled)"
                
                # Test generate_summary
                res = await service.generate_summary(title, content)
                assert res["summary"] == ""
                assert res["key_points"] == []
                
                # Test extract_concepts
                res = await service.extract_concepts(title, content)
                assert res == []
                
                # Test generate_tags
                res = await service.generate_tags(title, content)
                assert res == []

    asyncio.run(run_test())
