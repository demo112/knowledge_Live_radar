
import pytest
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_property_14_transaction_atomicity(db_session):
    """Property 14: 事务原子性 (Transaction Atomicity)"""
    service = PyramidService(db_session)

    # Setup
    pyramid = await service.create_pyramid(PyramidCreate(name="Atomicity Test"))
    node = await service.add_node(pyramid.id, PyramidNodeCreate(name="Node", sort_order=0))
    
    # Attempt to move node to itself (invalid) BUT also update sort_order
    # move_node updates sort_order first, then checks parent validity.
    # If check fails, commit should not happen.
    
    with pytest.raises(HTTPException) as excinfo:
        await service.move_node(node.id, new_parent_id=node.id, new_sort_order=999)
        
    assert excinfo.value.status_code == 400
    assert "不能移动节点到自身" in excinfo.value.detail
    
    # Verify DB state
    # We need to expire the object or clear session to ensure we fetch from DB
    node_id = node.id
    db_session.expire_all()
    
    fetched_node = await service.get_node(node_id)
    assert fetched_node.sort_order == 0 # Should NOT be 999
