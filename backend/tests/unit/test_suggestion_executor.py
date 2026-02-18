import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

from app.services.suggestion_executor import SuggestionExecutor
from app.models.ai_suggestion import AISuggestion
from app.models.pyramid import PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.source import InformationSource


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def executor(mock_db):
    return SuggestionExecutor(mock_db)


@pytest.mark.asyncio
async def test_approve_suggestion_success(executor, mock_db):
    suggestion_id = uuid.uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        status="pending",
        action_type="create_node",
        reason="测试建议",
        params={},
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = suggestion
    mock_db.execute.return_value = mock_result

    result = await executor.approve(str(suggestion_id), mock_db)

    assert result["success"] is True
    assert result["data"]["status"] == "approved"
    assert suggestion.status == "approved"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_approve_suggestion_not_pending(executor, mock_db):
    suggestion_id = uuid.uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="create_node",
        reason="测试建议",
        params={},
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = suggestion
    mock_db.execute.return_value = mock_result

    result = await executor.approve(str(suggestion_id), mock_db)

    assert result["success"] is False
    assert "ERR_SUGGESTION_NOT_PENDING" in result["error"]["code"]


@pytest.mark.asyncio
async def test_reject_suggestion_success(executor, mock_db):
    suggestion_id = uuid.uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        status="pending",
        action_type="create_node",
        reason="测试建议",
        params={},
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = suggestion
    mock_db.execute.return_value = mock_result

    result = await executor.reject(str(suggestion_id), mock_db, reason="不符合要求")

    assert result["success"] is True
    assert result["data"]["status"] == "rejected"
    assert suggestion.status == "rejected"
    assert "不符合要求" in suggestion.reason
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_execute_suggestion_not_approved(executor, mock_db):
    suggestion_id = uuid.uuid4()
    suggestion = AISuggestion(
        id=suggestion_id,
        status="pending",
        action_type="create_node",
        reason="测试建议",
        params={},
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = suggestion
    mock_db.execute.return_value = mock_result

    result = await executor.execute(str(suggestion_id), mock_db)

    assert result["success"] is False
    assert "ERR_SUGGESTION_NOT_APPROVED" in result["error"]["code"]


@pytest.mark.asyncio
async def test_execute_create_node(executor, mock_db):
    suggestion_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()
    parent_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="create_node",
        reason="需要新节点",
        params={
            "pyramid_id": str(pyramid_id),
            "parent_id": str(parent_id),
            "name": "新节点",
            "description": "节点描述",
        },
    )

    parent_node = PyramidNode(
        id=parent_id,
        pyramid_id=pyramid_id,
        name="父节点",
        level=1,
        path="",
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=parent_node):
            with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                with patch.object(executor, 'snapshot_service') as mock_snapshot:
                    mock_snapshot.create_snapshot = AsyncMock()
                    mock_db.add = MagicMock()

                    result = await executor.execute(str(suggestion_id), mock_db)

                    assert result["success"] is True
                    assert result["data"]["action"] == "create_node"
                    mock_db.add.assert_called_once()
                    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_execute_delete_node(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="delete_node",
        reason="节点已过时",
        params={
            "node_id": str(node_id),
        },
        pyramid_id=pyramid_id,
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="待删除节点",
        level=1,
        is_deleted=False,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=node):
            with patch.object(executor, '_get_node_children', return_value=[]):
                with patch.object(executor, '_get_content_relations', return_value=[]):
                    with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                        with patch.object(executor, 'snapshot_service') as mock_snapshot:
                            mock_snapshot.create_snapshot = AsyncMock()

                            result = await executor.execute(str(suggestion_id), mock_db)

                            assert result["success"] is True
                            assert result["data"]["action"] == "delete_node"
                            assert node.is_deleted is True


@pytest.mark.asyncio
async def test_execute_update_node(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="update_node",
        reason="更新节点名称",
        params={
            "node_id": str(node_id),
            "name": "新名称",
            "description": "新描述",
        },
        pyramid_id=pyramid_id,
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="旧名称",
        description="旧描述",
        level=1,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=node):
            with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                with patch.object(executor, 'snapshot_service') as mock_snapshot:
                    mock_snapshot.create_snapshot = AsyncMock()

                    result = await executor.execute(str(suggestion_id), mock_db)

                    assert result["success"] is True
                    assert result["data"]["action"] == "update_node"
                    assert node.name == "新名称"
                    assert node.description == "新描述"


@pytest.mark.asyncio
async def test_execute_split_node(executor, mock_db):
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
            "suggested_children": ["子节点A", "子节点B", "子节点C"],
        },
        pyramid_id=pyramid_id,
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="待拆分节点",
        level=1,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=node):
            with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                with patch.object(executor, 'snapshot_service') as mock_snapshot:
                    mock_snapshot.create_snapshot = AsyncMock()
                    mock_db.add = MagicMock()

                    result = await executor.execute(str(suggestion_id), mock_db)

                    assert result["success"] is True
                    assert result["data"]["action"] == "split_node"
                    assert len(result["data"]["created_children"]) == 3


@pytest.mark.asyncio
async def test_execute_link_content(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    content_id1 = uuid.uuid4()
    content_id2 = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="link_content",
        reason="内容与节点相关",
        params={
            "node_id": str(node_id),
            "content_ids": [str(content_id1), str(content_id2)],
        },
        pyramid_id=pyramid_id,
        confidence=0.85,
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="目标节点",
        level=1,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=node):
            with patch.object(executor, '_get_content_relation', return_value=None):
                with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                    with patch.object(executor, 'snapshot_service') as mock_snapshot:
                        mock_snapshot.create_snapshot = AsyncMock()
                        mock_db.add = MagicMock()

                        result = await executor.execute(str(suggestion_id), mock_db)

                        assert result["success"] is True
                        assert result["data"]["action"] == "link_content"
                        assert result["data"]["linked_count"] == 2


@pytest.mark.asyncio
async def test_execute_update_strategy(executor, mock_db):
    suggestion_id = uuid.uuid4()
    source_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="update_strategy",
        reason="抓取频率过低",
        params={
            "source_id": str(source_id),
            "new_interval": 1800,
        },
    )

    source = InformationSource(
        id=source_id,
        name="测试信息源",
        type="RSS",
        url="https://example.com/feed",
        check_interval=3600,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_source', return_value=source):
            with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=None):
                with patch.object(executor, 'snapshot_service') as mock_snapshot:
                    mock_snapshot.create_snapshot = AsyncMock()

                    result = await executor.execute(str(suggestion_id), mock_db)

                    assert result["success"] is True
                    assert result["data"]["action"] == "update_strategy"
                    assert source.check_interval == 1800


@pytest.mark.asyncio
async def test_execute_archive_content(executor, mock_db):
    suggestion_id = uuid.uuid4()
    content_id1 = uuid.uuid4()
    content_id2 = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="archive_content",
        reason="内容已过时",
        params={
            "content_ids": [str(content_id1), str(content_id2)],
        },
    )

    content1 = ContentItem(
        id=content_id1,
        title="内容1",
        url="https://example.com/1",
        lifecycle_status="ACTIVE",
    )
    content2 = ContentItem(
        id=content_id2,
        title="内容2",
        url="https://example.com/2",
        lifecycle_status="ACTIVE",
    )

    content_iter = iter([content1, content2])

    def mock_get_content(cid):
        return next(content_iter, None)

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_content', side_effect=mock_get_content):
            with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=None):
                with patch.object(executor, 'snapshot_service') as mock_snapshot:
                    mock_snapshot.create_snapshot = AsyncMock()

                    result = await executor.execute(str(suggestion_id), mock_db)

                    assert result["success"] is True
                    assert result["data"]["action"] == "archive_content"
                    assert result["data"]["archived_count"] == 2


@pytest.mark.asyncio
async def test_execute_unknown_action_type(executor, mock_db):
    suggestion_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="unknown_action",
        reason="未知操作",
        params={},
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=None):
            with patch.object(executor, 'snapshot_service') as mock_snapshot:
                mock_snapshot.create_snapshot = AsyncMock()

                result = await executor.execute(str(suggestion_id), mock_db)

                assert result["success"] is False
                assert "ERR_UNKNOWN_ACTION_TYPE" in result["error"]["code"]


@pytest.mark.asyncio
async def test_suggestion_not_found(executor, mock_db):
    with patch.object(executor, '_get_suggestion', return_value=None):
        result = await executor.approve(str(uuid.uuid4()), mock_db)

        assert result["success"] is False
        assert "ERR_SUGGESTION_NOT_FOUND" in result["error"]["code"]


@pytest.mark.asyncio
async def test_execute_merge_node(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="merge_node",
        reason="节点内容稀疏",
        params={
            "node_id": str(node_id),
        },
        pyramid_id=pyramid_id,
    )

    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="待合并节点",
        level=1,
        is_deleted=False,
    )

    child1 = PyramidNode(
        id=uuid.uuid4(),
        pyramid_id=pyramid_id,
        name="子节点1",
        level=2,
        parent_id=node_id,
    )

    with patch.object(executor, '_get_suggestion', return_value=suggestion):
        with patch.object(executor, '_get_node', return_value=node):
            with patch.object(executor, '_get_node_children', return_value=[child1]):
                with patch.object(executor, '_get_content_relations', return_value=[]):
                    with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                        with patch.object(executor, 'snapshot_service') as mock_snapshot:
                            mock_snapshot.create_snapshot = AsyncMock()

                            result = await executor.execute(str(suggestion_id), mock_db)

                            assert result["success"] is True
                            assert result["data"]["action"] == "merge_node"
                            assert node.is_deleted is True
                            assert child1.parent_id is None
