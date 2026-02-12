import pytest
import pytest_asyncio
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
from sqlalchemy import select
from app.models.pyramid import Pyramid

@pytest.mark.asyncio
async def test_property_14_transaction_atomicity(db_session):
    """Property 14: 事务原子性 (Transaction Atomicity)"""
    service = PyramidService(db_session)
    
    # Scene: Create pyramid and add node. If node creation fails, pyramid creation should ideally be rolled back?
    # Or more commonly in service layer: A complex operation like 'create_template' which does multiple inserts.
    
    # Since we don't have a multi-step single-transaction method yet (except maybe move_node which updates descendants),
    # let's test a hypothetical failure scenario or verify session behavior.
    
    # Let's simulate a failure in a manually controlled transaction block
    
    initial_count = 0
    result = await db_session.execute(select(Pyramid))
    initial_count = len(result.scalars().all())
    
    # We must ensure the session is not in a failed state before starting
    # But since fixtures handle session, it should be clean.
    
    try:
        # Use begin_nested() for a savepoint
        async with db_session.begin_nested():
             await service.create_pyramid(PyramidCreate(name="To Be Rolled Back"))
             # Force failure
             raise RuntimeError("Simulated Failure")
    except RuntimeError:
        # The inner block raised, so the savepoint should be rolled back.
        # But we need to ensure the outer transaction is still valid or handle it.
        pass
        
    # Verify rollback of the nested transaction
    # Since we caught the exception, the outer session might be active but the nested one rolled back.
    
    result = await db_session.execute(select(Pyramid))
    final_count = len(result.scalars().all())
    
    assert final_count == initial_count
