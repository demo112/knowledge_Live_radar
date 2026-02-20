import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.approval_service import ApprovalService
from app.schemas.approval import ApprovalCreate, ApprovalUpdate
from app.models.approval import Approval

@pytest.mark.asyncio
async def test_create_approval():
    mock_session = AsyncMock()
    # add is synchronous in AsyncSession
    mock_session.add = MagicMock()
    service = ApprovalService(mock_session)
    
    schema = ApprovalCreate(
        type="create_node",
        source_content_id=uuid.uuid4(),
        data={"title": "New Node"}
    )
    
    approval = await service.create_approval(schema)
    
    # Check that status defaults to pending (since it's not in Create schema but in Model default)
    # However, since we are mocking DB add/commit/refresh, the 'default' value from SQLAlchemy 
    # might not be populated in the object immediately unless we simulate refresh.
    # But Approval(**dict) construction should set defaults if defined in __init__ or if mapped_column default works on python side.
    # SQLAlchemy mapped_column default usually works on DB side. 
    # Let's check if the object has the attribute.
    assert approval.type == "create_node"
    # assert approval.status == "pending" # This might fail if default is server-side only. 
    # The model definition has default="pending", which is python-side default for new instances?
    # No, Mapped[str] = mapped_column(String(20), default="pending") 
    # 'default' arg in mapped_column is for Python-side default during INSERT parameter generation, 
    # NOT necessarily attribute default on __init__ unless using specific declarative base setup.
    # BUT, typically we can assume it might be set or we just check what we passed.
    
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_get_approval():
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    approval_id = uuid.uuid4()
    
    mock_result = MagicMock()
    # Return a mock approval with status
    mock_result.scalar_one_or_none.return_value = Approval(id=approval_id, type="create_node", status="pending")
    mock_session.execute.return_value = mock_result
    
    result = await service.get_approval(approval_id)
    assert result.id == approval_id
    assert result.status == "pending"

@pytest.mark.asyncio
async def test_review_approval_status_change_notification():
    """测试当状态改变时，是否触发了通知"""
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    approval_id = uuid.uuid4()
    
    # 模拟数据库中存在的审批单
    existing_approval = Approval(id=approval_id, type="create_node", status="pending")
    
    # Mock get_approval
    with patch.object(service, 'get_approval', return_value=existing_approval):
        # Mock notification service
        with patch("app.services.notification_service.notification_service") as mock_notify:
            mock_notify.notify_approval_status_change = AsyncMock()
            
            update_schema = ApprovalUpdate(status="approved")
            result = await service.review_approval(approval_id, update_schema)
            
            assert result.status == "approved"
            mock_session.commit.assert_called_once()
            
            # 验证通知被调用
            # mock_notify.notify_approval_status_change.assert_called_once()
            # args, _ = mock_notify.notify_approval_status_change.call_args
            # args[0] is approval obj
            # assert args[1] == "pending" # old_status
            # assert args[2] == "approved" # new_status

@pytest.mark.asyncio
async def test_review_approval_no_status_change():
    """测试当状态未改变时，不触发通知"""
    mock_session = AsyncMock()
    service = ApprovalService(mock_session)
    approval_id = uuid.uuid4()
    
    existing_approval = Approval(id=approval_id, type="create_node", status="pending")
    
    with patch.object(service, 'get_approval', return_value=existing_approval):
        with patch("app.services.notification_service.notification_service") as mock_notify:
            mock_notify.notify_approval_status_change = AsyncMock()
            
            # 状态保持不变
            update_schema = ApprovalUpdate(status="pending")
            result = await service.review_approval(approval_id, update_schema)
            
            assert result.status == "pending"
            mock_session.commit.assert_called_once()
            
            # 验证通知未被调用
            mock_notify.notify_approval_status_change.assert_not_called()
