import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.suggestion_executor import SuggestionExecutor
from app.models.ai_suggestion import AISuggestion
from app.models.pyramid import PyramidNode

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def executor(mock_db):
    return SuggestionExecutor(mock_db)

@pytest.mark.asyncio
async def test_execute_split_node_sets_path(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="split_node",
        reason="节点内容过多",
        params={
            "node_id": str(node_id),
            "suggested_children": ["子节点A", "子节点B"],
        },
        pyramid_id=pyramid_id,
        target_id=node_id
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="待拆分节点",
        level=1,
        path="/root_id/"
    )

    # Mock async methods
    executor._get_suggestion = AsyncMock(return_value=suggestion)
    executor._get_node = AsyncMock(return_value=node)
    executor._get_pyramid_id_for_suggestion = AsyncMock(return_value=pyramid_id)
    executor.snapshot_service = MagicMock()
    executor.snapshot_service.create_snapshot = AsyncMock()
    
    # Mock db add/flush
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    # Execute
    result = await executor.execute(str(suggestion_id), mock_db)

    # Verify
    assert result["success"] is True
    assert result["data"]["action"] == "split_node"
    
    # Verify children creation
    # add() is called for each child
    assert mock_db.add.call_count == 2
    
    calls = mock_db.add.call_args_list
    for call in calls:
        child = call[0][0]
        assert isinstance(child, PyramidNode)
        assert child.path is not None
        # Check path format - should contain parent id
        # Expected: /root_id/ + node_id + /
        expected_path_part = f"{node.path}{node.id}/"
        # Or at least contains node_id
        assert str(node_id) in child.path

@pytest.mark.asyncio
async def test_execute_merge_node_sets_path(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node1_id = uuid.uuid4()
    node2_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    
    parent_path = "/root/"

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="merge_node",
        reason="节点内容稀疏",
        params={
            "source_node_ids": [str(node1_id), str(node2_id)],
            "target_node_name": "合并节点",
            "pyramid_id": str(pyramid_id)
        },
        pyramid_id=pyramid_id,
    )

    node1 = PyramidNode(
        id=node1_id,
        pyramid_id=pyramid_id,
        name="节点1",
        level=2,
        parent_id=parent_id,
        path=parent_path
    )
    
    node2 = PyramidNode(
        id=node2_id,
        pyramid_id=pyramid_id,
        name="节点2",
        level=2,
        parent_id=parent_id,
        path=parent_path
    )
    
    child = PyramidNode(id=uuid.uuid4(), pyramid_id=pyramid_id, parent_id=node1_id)

    # Mock async methods
    executor._get_suggestion = AsyncMock(return_value=suggestion)
    
    async def mock_get_node_side_effect(nid):
        nid_str = str(nid)
        if nid_str == str(node1_id): return node1
        if nid_str == str(node2_id): return node2
        return None
        
    executor._get_node = AsyncMock(side_effect=mock_get_node_side_effect)
    executor._get_node_children = AsyncMock(return_value=[child])
    executor._get_content_relations = AsyncMock(return_value=[])
    executor._check_relation_exists = AsyncMock(return_value=False)
    executor._get_pyramid_id_for_suggestion = AsyncMock(return_value=pyramid_id)
    executor.snapshot_service = MagicMock()
    executor.snapshot_service.create_snapshot = AsyncMock()
    
    mock_db.add = MagicMock()
    mock_db.delete = AsyncMock()
    mock_db.flush = AsyncMock()

    # Execute
    result = await executor.execute(str(suggestion_id), mock_db)

    # Verify
    assert result["success"] is True
    
    # Verify merged node creation
    # The first call to add should be the merged node
    # Note: DB calls might be ordered differently if implementation changes, but currently merged node is added first.
    merged_node = mock_db.add.call_args_list[0][0][0]
    assert isinstance(merged_node, PyramidNode)
    # The merged node should inherit path from siblings
    assert merged_node.path == parent_path
