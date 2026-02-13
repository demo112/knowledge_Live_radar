import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.validator import HardValidator, SoftValidator, CrossValidator
from app.models.content import ContentItem

@pytest.mark.asyncio
async def test_hard_validator():
    validator = HardValidator(min_length=5, banned_words=["bad"])
    
    # Valid
    valid, _ = await validator.validate({"title": "Good Title", "content": "Good Content"})
    assert valid
    
    # Too short
    valid, _ = await validator.validate({"title": "Hi", "content": "Lo"})
    assert not valid
    
    # Banned word
    valid, _ = await validator.validate({"title": "Test", "content": "This is bad"})
    assert not valid

    # Scunthorpe problem (should pass now)
    # "bad" is banned, but "badminton" should be allowed
    valid, _ = await validator.validate({"title": "Sport", "content": "I like badminton"})
    assert valid

@pytest.mark.asyncio
async def test_soft_validator():
    # Patch the ai_service instance in soft_validator module
    with patch("app.services.validator.soft_validator.ai_service") as mock_service:
        mock_service.client = True # Simulate client exists
        mock_service.validate_content_soft = AsyncMock()
        
        validator = SoftValidator()
        
        # AI says valid (Score 80)
        mock_service.validate_content_soft.return_value = {
            "score": 80,
            "reason": "This content is valid.",
            "dimensions": {}
        }
        valid, result = await validator.validate({"title": "Tech", "content": "AI is great"})
        assert valid
        assert result["score"] == 80
        
        # AI says invalid (Score 40)
        mock_service.validate_content_soft.return_value = {
            "score": 40,
            "reason": "No, this is unrelated.",
            "dimensions": {}
        }
        valid, result = await validator.validate({"title": "Cooking", "content": "Pasta recipe"})
        assert not valid
        assert result["score"] == 40

        # Boundary Test: Score 59 (Fail)
        mock_service.validate_content_soft.return_value = {
            "score": 59,
            "reason": "Almost there",
            "dimensions": {}
        }
        valid, _ = await validator.validate({"title": "Border", "content": "Test"})
        assert not valid

        # Boundary Test: Score 60 (Pass)
        mock_service.validate_content_soft.return_value = {
            "score": 60,
            "reason": "Just passed",
            "dimensions": {}
        }
        valid, _ = await validator.validate({"title": "Border", "content": "Test"})
        assert valid

@pytest.mark.asyncio
async def test_cross_validator():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    
    validator = CrossValidator(mock_session)
    
    # Unique
    mock_result.scalar_one_or_none.return_value = None
    valid, _ = await validator.validate({"url": "http://unique.com"})
    assert valid
    
    # Duplicate
    mock_result.scalar_one_or_none.return_value = ContentItem(id="123")
    valid, _ = await validator.validate({"url": "http://duplicate.com"})
    assert not valid
