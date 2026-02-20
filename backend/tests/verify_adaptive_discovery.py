
import asyncio
import sys
import os
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend path to sys.path
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.services.source_discovery import SourceDiscoveryService
from app.models.pyramid import Pyramid, PyramidNode
from app.models.approval import Approval

async def test_adaptive_discovery():
    print("🚀 Starting Adaptive Discovery Verification...")

    # 1. Mock DB and Pyramid Structure
    mock_db = AsyncMock()
    
    pyramid_id = uuid.uuid4()
    
    # Create nodes with explicit parent_id relationships
    root_id = uuid.uuid4()
    branch_a_id = uuid.uuid4()
    branch_b_id = uuid.uuid4()
    leaf_a1_id = uuid.uuid4()
    deep_leaf_a1_1_id = uuid.uuid4()
    
    nodes = [
        PyramidNode(id=root_id, name="Root Technology", level=1, parent_id=None, pyramid_id=pyramid_id, sort_order=0, is_deleted=False),
        PyramidNode(id=branch_a_id, name="Branch A", level=2, parent_id=root_id, pyramid_id=pyramid_id, sort_order=0, is_deleted=False),
        PyramidNode(id=branch_b_id, name="Branch B", level=2, parent_id=root_id, pyramid_id=pyramid_id, sort_order=1, is_deleted=False),
        PyramidNode(id=leaf_a1_id, name="Leaf A1", level=3, parent_id=branch_a_id, pyramid_id=pyramid_id, sort_order=0, is_deleted=False),
        PyramidNode(id=uuid.uuid4(), name="Leaf A2", level=3, parent_id=branch_a_id, pyramid_id=pyramid_id, sort_order=1, is_deleted=False),
        PyramidNode(id=uuid.uuid4(), name="Leaf B1", level=3, parent_id=branch_b_id, pyramid_id=pyramid_id, sort_order=0, is_deleted=False),
        # Deep leaf (Level 4) - Should be pruned by depth limit 3
        PyramidNode(id=deep_leaf_a1_1_id, name="Deep Leaf A1-1", level=4, parent_id=leaf_a1_id, pyramid_id=pyramid_id, sort_order=0, is_deleted=False)
    ]
    
    mock_pyramid = Pyramid(
        id=pyramid_id,
        name="Test Pyramid",
        description="A test pyramid for verification"
    )

    # Mock DB execution results
    # Call 1: Get Pyramid -> returns mock_pyramid
    # Call 2: Get Nodes -> returns list of nodes
    # Call 3: Check existing Approvals (during loop) -> returns empty
    
    # PATCH Approval.data to support .astext access for the test
    # This is needed because SQLAlchemy's generic JSON type might not expose .astext
    # unless using PG dialect, and in test env we want to avoid AttributeErrors.
    original_data_col = Approval.data
    mock_data_col = MagicMock()
    # Support dictionary access: Approval.data['url']
    mock_data_col.__getitem__.return_value = MagicMock() 
    # Support .astext: Approval.data['url'].astext
    mock_data_col.__getitem__.return_value.astext = MagicMock()
    
    # We need to patch the class attribute. 
    # Since it's a mapped column, patching it might be tricky.
    # Instead of patching the model, let's try to patch the specific line in source_discovery.py?
    # No, that's hard.
    
    # Let's try patching Approval.data on the class.
    patcher = patch.object(Approval, 'data', mock_data_col)
    patcher.start()

    mock_result_pyramid = MagicMock()
    mock_result_pyramid.scalar_one_or_none.return_value = mock_pyramid
    
    mock_result_nodes = MagicMock()
    mock_result_nodes.scalars.return_value.all.return_value = nodes
    
    mock_result_empty = MagicMock()
    mock_result_empty.scalar_one_or_none.return_value = None
 
    # Use side_effect to return different results based on call order
    # Note: execute is awaited, so side_effect should be an iterable of return values (or callables)
    # Since it's an AsyncMock, the side_effect should return the result directly if it's not a coroutine, 
    # but here execute returns a ResultProxy/Result object.
    
    # Actually, we can check the query structure to distinguish, but side_effect is easier for sequential calls.
    # The sequence in discover_stream is:
    # 1. _get_structure_snapshot -> execute(select(Pyramid))
    # 2. _get_structure_snapshot -> execute(select(PyramidNode))
    # 3. For each candidate -> execute(select(Approval).where(...))
    
    # We need a generator for side_effect
    def db_execute_side_effect(*args, **kwargs):
        # Identify query type by inspecting args[0] (the statement)
        # This is robust but complex. Simple list iterator is risky if calls change.
        # Let's try to infer from the query if possible, or just use sequence.
        stmt = args[0]
        stmt_str = str(stmt)
        
        # When mocked, str(stmt) might be just the mock string if the column is mocked?
        # If Approval.data is mocked, the expression using it might be a mock expression.
        
        if "FROM pyramid" in stmt_str and "JOIN" not in stmt_str: # Simple check
            return mock_result_pyramid
        elif "FROM pyramid_node" in stmt_str:
            return mock_result_nodes
        # Since Approval.data is mocked, the query string might not contain "FROM approval" 
        # if the mock expression doesn't stringify to standard SQL.
        # But select(Approval) should still work.
        elif "FROM approval" in stmt_str or "approvals" in stmt_str:
            return mock_result_empty
        else:
            # Fallback for mocked approval query
            return mock_result_empty

    mock_db.execute.side_effect = db_execute_side_effect
  
    # 2. Initialize Service
    service = SourceDiscoveryService(mock_db)
    
    # Mock AIFacade
    service.ai = AsyncMock()
    mock_queries = [
        {"query": "Macro Query 1", "intent": "overview", "scope": "Macro", "reason": "Test Reason 1"},
        {"query": "Meso Query 1", "intent": "deep_dive", "scope": "Meso", "reason": "Test Reason 2"},
        {"query": "Micro Query 1", "intent": "specific", "scope": "Micro", "reason": "Test Reason 3"}
    ]
    service.ai.generate_adaptive_queries.return_value = mock_queries

    # Mock DDGS (Search Engine)
    service.ddgs = MagicMock()
    service.ddgs.text.return_value = [
        {"href": "http://example.com/macro", "title": "Macro Result", "body": "Description 1"},
        {"href": "http://example.com/meso", "title": "Meso Result", "body": "Description 2"}
    ]

    # 3. Run Discovery Stream
    print(f"\nrunning discovery for pyramid: {pyramid_id}")
    
    events_received = []
    try:
        async for event in service.discover_stream(pyramid_id):
            print(f"Event: {event.event} | Data: {str(event.data)[:100]}...")
            events_received.append(event)
            
            if event.event == "error":
                print(f"❌ Error received: {event.data}")
    except Exception as e:
        print(f"❌ Exception during stream: {e}")
        import traceback
        traceback.print_exc()

    # 4. Verify Results
    print("\n🔍 Verification Results:")
    
    # Verify AI was called and check snapshot structure (Pruning)
    if service.ai.generate_adaptive_queries.called:
        print("✅ AI generate_adaptive_queries was called.")
        args = service.ai.generate_adaptive_queries.call_args
        # args[0] is (pyramid_name, pyramid_structure_json)
        snapshot_json = args[0][1]
        snapshot = json.loads(snapshot_json)
        
        print("   Snapshot extracted successfully.")
        
        # Verify pruning: Deep Leaf A1-1 (Level 4) should NOT be in the snapshot
        # Structure: Root -> Branch A -> Leaf A1 -> [Children should be empty]
        
        roots = snapshot.get("structure")
        if isinstance(roots, list):
            print(f"   Structure is list with {len(roots)} roots.")
            root = roots[0]
        else:
            root = roots
            
        print(f"   Root: {root['name']}")
        
        # Navigate to Branch A
        branch_a = next((c for c in root['children'] if c['name'] == 'Branch A'), None)
        if branch_a:
            print("   Found Branch A")
            leaf_a1 = next((c for c in branch_a['children'] if c['name'] == 'Leaf A1'), None)
            if leaf_a1:
                print("   Found Leaf A1")
                if not leaf_a1['children']:
                    print("✅ Pruning Verified: Leaf A1 has no children (Deep Leaf removed).")
                else:
                    print(f"❌ Pruning Failed: Leaf A1 has children: {leaf_a1['children']}")
            else:
                print("❌ Leaf A1 not found in snapshot.")
        else:
            print("❌ Branch A not found in snapshot.")
            
    else:
        print("❌ AI generate_adaptive_queries was NOT called.")

    # Verify Search was called
    if service.ddgs.text.called:
        print(f"✅ DDGS search was called {service.ddgs.text.call_count} times.")
    else:
        print("❌ DDGS search was NOT called.")

    # Verify Events
    stage_updates = [e for e in events_received if e.event == "stage_update"]
    print(f"✅ Received {len(stage_updates)} stage updates.")
    
    progress_events = [e for e in events_received if e.event == "progress"]
    print(f"✅ Received {len(progress_events)} progress events.")
    
    result_events = [e for e in events_received if e.event == "result"]
    print(f"✅ Received {len(result_events)} result events (candidates).")
    
    if len(result_events) > 0:
        print("✅ Flow completed successfully.")
    else:
        print("⚠️ Flow completed but no results found (might be due to deduplication or mocking).")

if __name__ == "__main__":
    asyncio.run(test_adaptive_discovery())
