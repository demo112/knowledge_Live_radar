import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.whitelist_service import WhitelistService
from app.models.domain_whitelist import DomainWhitelist

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def whitelist_service(mock_db_session):
    return WhitelistService(mock_db_session)

@pytest.mark.asyncio
async def test_add_domain_new(whitelist_service, mock_db_session):
    domain = "example.com"
    credibility = 80
    
    # Mock not found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    result = await whitelist_service.add_domain(domain, credibility)
    
    assert result.domain == domain
    assert result.credibility == credibility
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()

@pytest.mark.asyncio
async def test_add_domain_existing(whitelist_service, mock_db_session):
    domain = "example.com"
    credibility = 90
    
    existing_domain = MagicMock()
    existing_domain.domain = domain
    existing_domain.credibility = 50
    existing_domain.is_deleted = True
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_domain
    mock_db_session.execute.return_value = mock_result
    
    result = await whitelist_service.add_domain(domain, credibility)
    
    assert result.credibility == credibility
    assert not result.is_deleted
    mock_db_session.commit.assert_called()

@pytest.mark.asyncio
async def test_check_domain_exact(whitelist_service, mock_db_session):
    domain = "example.com"
    
    mock_match = MagicMock()
    mock_match.credibility = 75
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_match
    mock_db_session.execute.return_value = mock_result
    
    is_whitelisted, credibility = await whitelist_service.check_domain(domain)
    
    assert is_whitelisted
    assert credibility == 75

@pytest.mark.asyncio
async def test_check_domain_wildcard(whitelist_service, mock_db_session):
    domain = "sub.example.com"
    
    # First query (exact) returns None
    # Second query (wildcard) returns list
    mock_result_exact = MagicMock()
    mock_result_exact.scalar_one_or_none.return_value = None
    
    mock_wildcard = MagicMock()
    mock_wildcard.domain = "*.example.com"
    mock_wildcard.credibility = 60
    
    mock_result_wildcard = MagicMock()
    mock_result_wildcard.scalars.return_value.all.return_value = [mock_wildcard]
    
    mock_db_session.execute.side_effect = [mock_result_exact, mock_result_wildcard]
    
    is_whitelisted, credibility = await whitelist_service.check_domain(domain)
    
    assert is_whitelisted
    assert credibility == 60

@pytest.mark.asyncio
async def test_check_domain_not_found(whitelist_service, mock_db_session):
    domain = "unknown.com"
    
    mock_result_exact = MagicMock()
    mock_result_exact.scalar_one_or_none.return_value = None
    
    mock_result_wildcard = MagicMock()
    mock_result_wildcard.scalars.return_value.all.return_value = []
    
    mock_db_session.execute.side_effect = [mock_result_exact, mock_result_wildcard]
    
    is_whitelisted, credibility = await whitelist_service.check_domain(domain)
    
    assert not is_whitelisted
    assert credibility == 0

@pytest.mark.asyncio
async def test_remove_domain(whitelist_service, mock_db_session):
    domain_id = uuid4()
    
    mock_domain = MagicMock()
    mock_domain.domain = "example.com"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_domain
    mock_db_session.execute.return_value = mock_result
    
    result = await whitelist_service.remove_domain(domain_id)
    
    assert result
    assert mock_domain.is_deleted
    mock_db_session.commit.assert_called()
