import pytest
from unittest.mock import AsyncMock, patch
from app.services.notification_service import notification_service
from app.models.approval import Approval
import uuid

@pytest.mark.asyncio
async def test_notify_approval_status_change():
    approval = Approval(
        id=uuid.uuid4(),
        type="create_node",
        status="approved",
        applicant_id="user123",
        data={}
    )
    
    with patch("app.services.notification_service.logger") as mock_logger:
        await notification_service.notify_approval_status_change(approval, "pending", "approved")
        
        # Verify logger was called
        assert mock_logger.info.call_count >= 1
        call_args = mock_logger.info.call_args_list[0][0][0]
        assert "status changed from pending to approved" in call_args
