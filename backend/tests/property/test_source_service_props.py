import pytest
import pytest_asyncio
from hypothesis import given, strategies as st
from app.services.source_service import SourceService
from app.schemas.source import SourceCreate, SourceUpdate
from app.models.source import InformationSource
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_property_12_source_url_uniqueness(db_session):
    """Property 12: 信息源 URL 唯一性 (URL Uniqueness)"""
    service = SourceService(db_session)
    
    url = "https://example.com/unique"
    
    # Create first
    await service.create_source(SourceCreate(name="Source 1", url=url, type="RSS"))
    
    # Try create second with same URL
    with pytest.raises(HTTPException) as excinfo:
        await service.create_source(SourceCreate(name="Source 2", url=url, type="RSS"))
    
    assert excinfo.value.status_code == 400
    assert "already exists" in excinfo.value.detail

@pytest.mark.asyncio
async def test_property_13_source_update_isolation(db_session):
    """Property 13: 信息源更新隔离性 (Update Isolation)"""
    service = SourceService(db_session)
    
    # Setup
    source = await service.create_source(SourceCreate(name="Original", url="https://example.com/iso", type="RSS"))
    
    # Update
    new_name = "Updated Source"
    await service.update_source(source.id, SourceUpdate(name=new_name))
    
    # Verify
    updated = await service.get_source(source.id)
    assert updated.name == new_name
    assert updated.url == "https://example.com/iso" # Should not change
    
    # Verify no side effects on other sources (if any)
    # Create another source
    other = await service.create_source(SourceCreate(name="Other", url="https://example.com/other", type="RSS"))
    assert other.name == "Other"
