
import pytest
import uuid
from sqlalchemy import select
from app.models.pyramid import Pyramid, PyramidNode
from app.models.approval import Approval
from app.services.approval_service import ApprovalService

@pytest.mark.asyncio
async def test_execute_create_node_approval(db_session):
    # 1. Setup Data
    pyramid_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid")
    db_session.add(pyramid)
    
    parent_node = PyramidNode(
        id=parent_id, 
        pyramid_id=pyramid_id, 
        name="Parent Node", 
        level=0, 
        path=f"/root/{parent_id}"
    )
    db_session.add(parent_node)
    
    approval_id = uuid.uuid4()
    new_node_name = "New Child Node"
    
    approval = Approval(
        id=approval_id,
        type="create_node",
        status="approved",  # Must be approved to execute
        generated_by="ai",
        reason="Test reason",
        confidence_score=0.9,
        data={
            "name": new_node_name,
            "pyramid_id": str(pyramid_id),
            "description": "Test Description",
            "parent_id": str(parent_id)
        }
    )
    db_session.add(approval)
    await db_session.commit()
    
    # 2. Execute Approval
    service = ApprovalService(db_session)
    result = await service.execute_approval(approval_id)
    
    assert result is True
    
    # 3. Verify Execution
    # Check approval status
    await db_session.refresh(approval)
    assert approval.status == "executed"
    assert approval.executed_at is not None # DecisionExecutor might not set it if commented out, let's check code
    
    # Check new node created
    stmt = select(PyramidNode).where(PyramidNode.name == new_node_name)
    result_node = await db_session.execute(stmt)
    new_node = result_node.scalar_one_or_none()
    
    assert new_node is not None
    assert new_node.pyramid_id == pyramid_id
    assert new_node.parent_id == parent_id
    assert new_node.level == 1
    # Check path logic if implemented in DecisionExecutor
    # /root/{parent_id}/{new_node_id}
    expected_path_prefix = f"/root/{parent_id}/"
    assert new_node.path.startswith(expected_path_prefix)

@pytest.mark.asyncio
async def test_execute_link_content_approval(db_session):
    # 1. Setup Data
    pyramid_id = uuid.uuid4()
    node_id = uuid.uuid4()
    content_id = uuid.uuid4()
    
    pyramid = Pyramid(id=pyramid_id, name="Test Pyramid")
    db_session.add(pyramid)
    
    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        name="Target Node",
        level=0,
        path=f"/root/{node_id}"
    )
    db_session.add(node)
    
    # Need content item
    from app.models.content import ContentItem
    content = ContentItem(
        id=content_id,
        title="Test Content",
        url="http://test.com",
        status="processed"
    )
    db_session.add(content)
    
    approval_id = uuid.uuid4()
    
    approval = Approval(
        id=approval_id,
        type="link_content",
        status="approved",
        generated_by="ai",
        reason="Link reason",
        confidence_score=0.8,
        data={
            "node_id": str(node_id),
            "content_id": str(content_id),
            "confidence": 0.8
        }
    )
    db_session.add(approval)
    await db_session.commit()
    
    # 2. Execute
    service = ApprovalService(db_session)
    result = await service.execute_approval(approval_id)
    
    assert result is True
    
    # 3. Verify
    from app.models.content import ContentNodeRelation
    stmt = select(ContentNodeRelation).where(
        ContentNodeRelation.node_id == node_id,
        ContentNodeRelation.content_id == content_id
    )
    rel_result = await db_session.execute(stmt)
    relation = rel_result.scalar_one_or_none()
    
    assert relation is not None
    assert relation.confidence == 0.8
