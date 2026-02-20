import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.source_discovery import SourceDiscoveryService
from app.models.pyramid import Pyramid, PyramidNode
from app.models.approval import Approval
from app.schemas.source import DiscoveryEvent

@pytest.mark.asyncio
async def test_source_discovery_flow(db_session: AsyncSession):
    # 1. Setup Data
    pyramid_id = uuid.uuid4()
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid", description="A test pyramid")
    db_session.add(pyramid)
    
    # Root
    root_id = uuid.uuid4()
    root = PyramidNode(id=root_id, pyramid_id=pyramid_id, name="Root", level=1, node_type="Concept", sort_order=0, path=str(root_id))
    db_session.add(root)
    
    # Child
    child_id = uuid.uuid4()
    child = PyramidNode(id=child_id, pyramid_id=pyramid_id, parent_id=root_id, name="Child", level=2, node_type="Technology", sort_order=0, path=f"{root_id}.{child_id}")
    db_session.add(child)
    
    await db_session.commit()
    
    # 2. Mock Dependencies
    service = SourceDiscoveryService(db_session)
    
    # Mock AI
    mock_queries = [
        {"query": "Macro Query", "intent": "overview", "scope": "Macro", "reason": "Test Macro"},
        {"query": "Micro Query", "intent": "detail", "scope": "Micro", "reason": "Test Micro"}
    ]
    service.ai.generate_adaptive_queries = AsyncMock(return_value=mock_queries)
    
    # Mock DDGS
    mock_ddgs = MagicMock()
    # DDGS.text is synchronous, so we mock it as a regular method
    mock_ddgs.text.return_value = [
        {"href": "https://example.com/macro", "title": "Macro Result", "body": "Macro Body"},
        {"href": "https://example.com/micro", "title": "Micro Result", "body": "Micro Body"}
    ]
    service.ddgs = mock_ddgs
    
    # 3. Execute Discovery Stream
    events = []
    async for event in service.discover_stream(pyramid_id):
        events.append(event)
        
    # 4. Verify Events
    event_types = [e.event for e in events]
    assert "stage_update" in event_types
    assert "progress" in event_types
    assert "result" in event_types
    
    # Verify extraction
    # We can't easily check internal method calls unless we spy, but the flow completing implies success.
    
    # Verify AI call
    service.ai.generate_adaptive_queries.assert_called_once()
    call_args = service.ai.generate_adaptive_queries.call_args
    assert call_args[0][0] == "Test Pyramid" # name
    assert "Root (L1)" in call_args[0][1] # snapshot text
    assert "Child (L2)" in call_args[0][1]
    assert "[Technology]" in call_args[0][1] # node_type
    
    # Verify Search
    assert mock_ddgs.text.call_count == 2 # One for each query
    
    # Verify Approvals Created
    from sqlalchemy import select
    stmt = select(Approval).where(Approval.type == 'create_source')
    result = await db_session.execute(stmt)
    all_approvals = result.scalars().all()
    
    approvals = [a for a in all_approvals if a.data.get('pyramid_id') == str(pyramid_id)]
    assert len(approvals) == 2
    
    macro_approval = next(a for a in approvals if "Macro" in a.reason)
    assert macro_approval.data['url'] == "https://example.com/macro"
    assert "Macro" in macro_approval.reason

