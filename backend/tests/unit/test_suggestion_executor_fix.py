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
async def test_execute_link_content_missing_node_id_in_params(executor, mock_db):
    suggestion_id = uuid.uuid4()
    node_id = uuid.uuid4()
    content_id1 = uuid.uuid4()
    pyramid_id = uuid.uuid4()

    # Simulate the scenario where node_id is missing in params but target_id is set
    suggestion = AISuggestion(
        id=suggestion_id,
        status="approved",
        action_type="link_content",
        reason="内容与节点相关",
        params={
            # "node_id": str(node_id),  <-- Missing
            "content_ids": [str(content_id1)],
        },
        target_id=node_id,  # <-- Should fallback to this
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
            with patch.object(executor, '_check_relation_exists', return_value=False):
                with patch.object(executor, '_get_pyramid_id_for_suggestion', return_value=pyramid_id):
                    with patch.object(executor, 'snapshot_service') as mock_snapshot:
                        mock_snapshot.create_snapshot = AsyncMock()
                        mock_db.add = MagicMock()

                        result = await executor.execute(str(suggestion_id), mock_db)

                        assert result["success"] is True
                        assert result["data"]["action"] == "link_content"
                        assert result["data"]["node_id"] == str(node_id)
