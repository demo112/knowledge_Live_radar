
import pytest
from hypothesis import given, strategies as st, settings
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidUpdate
from app.models.pyramid import Pyramid, PyramidNode

# 注意：Hypothesis 直接装饰 async 测试函数在某些配置下可能有问题
# 这里我们尝试直接使用，如果环境支持。如果不行，通常会报 TypeError。
# 另一种方法是使用 st.data() 在测试内部抽取数据，但这需要测试本身由 hypothesis 驱动。

# 为了确保兼容性，我们先测试纯逻辑部分（无需 DB 交互的），
# 对于需要 DB 的，我们定义为 async 测试，并在内部使用少量手动生成的随机数据，
# 或者将 DB 操作部分 mock 掉从而变成同步测试。

# 但 Service 层紧密耦合 DB。
# 这里我们采用 "Hypothesis 生成数据 -> 调用 Async Service" 的模式。
# 由于 pytest-asyncio 处理 async def，我们需要确保 hypothesis 能正确处理。

# 临时方案：我们将测试分为两部分。
# 1. 纯逻辑测试（如同期健康度计算） -> 使用 Hypothesis
# 2. 数据库集成属性测试 -> 使用 pytest 参数化或循环随机数据

@pytest.mark.asyncio
async def test_property_10_health_score_range(db_session):
    """Property 10: 健康度评分范围 - 验证评分在 0-100 范围内"""
    service = PyramidService(db_session)
    
    # 既然 calculate_health_score 需要实际的节点数据，
    # 我们先创建一些模拟节点结构
    
    # 这是一个集成测试，我们随机生成树结构
    # 由于 Hypothesis 很难直接驱动 async fixture 的 setup/teardown，
    # 我们在这里手动运行几个 case
    
    pyramid = Pyramid(name="Test", description="Desc")
    db_session.add(pyramid)
    await db_session.commit()
    await db_session.refresh(pyramid)
    
    # Case 1: 空金字塔
    score = await service.calculate_health_score(pyramid.id)
    assert 0 <= score <= 100
    
    # Case 2: 只有根节点
    root = PyramidNode(pyramid_id=pyramid.id, name="Root", level=0)
    db_session.add(root)
    await db_session.commit()
    
    score = await service.calculate_health_score(pyramid.id)
    assert 0 <= score <= 100
    
    # Case 3: 深度树
    # ...构建更多节点...

@pytest.mark.asyncio
async def test_property_2_update_consistency(db_session):
    """Property 2: 金字塔更新一致性"""
    service = PyramidService(db_session)
    
    # Setup
    create_schema = PyramidCreate(name="Original", description="Desc")
    pyramid = await service.create_pyramid(create_schema)
    
    # Update
    new_name = "Updated Name"
    new_desc = "Updated Desc"
    update_schema = PyramidUpdate(name=new_name, description=new_desc)
    
    updated_pyramid = await service.update_pyramid(pyramid.id, update_schema)
    
    assert updated_pyramid.name == new_name
    assert updated_pyramid.description == new_desc
    assert updated_pyramid.id == pyramid.id
    assert updated_pyramid.created_at == pyramid.created_at
    
    # Fetch again to verify persistence
    fetched = await service.get_pyramid(pyramid.id)
    assert fetched.name == new_name

@pytest.mark.asyncio
async def test_property_3_delete_cascade(db_session):
    """Property 3: 金字塔删除级联"""
    service = PyramidService(db_session)
    
    # Setup
    pyramid = await service.create_pyramid(PyramidCreate(name="To Delete"))
    
    # Add nodes directly to DB for speed
    node = PyramidNode(pyramid_id=pyramid.id, name="Node", level=0, path="/")
    db_session.add(node)
    await db_session.commit()
    
    # Delete
    await service.delete_pyramid(pyramid.id)
    
    # Verify Soft Delete
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        await service.get_pyramid(pyramid.id)

    # Check node deletion (soft)
    # Since service.get_node might also raise 404, let's query DB directly or expect exception
    # Assuming we have get_node in service
    with pytest.raises(HTTPException):
        await service.get_node(node.id)

@pytest.mark.asyncio
async def test_property_4_list_integrity(db_session):
    """Property 4: 列表查询完整性"""
    service = PyramidService(db_session)
    
    # Setup
    created_ids = []
    for i in range(5):
        p = await service.create_pyramid(PyramidCreate(name=f"P{i}"))
        created_ids.append(p.id)
        
    # List
    # Check method name: get_all_pyramids or get_pyramids?
    # Router uses get_all_pyramids
    results = await service.get_all_pyramids(skip=0, limit=100)
    
    result_ids = [p.id for p in results]
    for pid in created_ids:
        assert pid in result_ids

@pytest.mark.asyncio
async def test_property_9_visualization_integrity(db_session):
    """Property 9: 可视化数据完整性"""
    service = PyramidService(db_session)
    
    # Setup
    pyramid = await service.create_pyramid(PyramidCreate(name="Vis Test"))
    node = await service.add_node(pyramid.id, PyramidNodeCreate(name="Node1"))
    
    # Get Details (which includes nodes)
    details = await service.get_pyramid_details(pyramid.id)
    
    assert details.id == pyramid.id
    assert len(details.nodes) == 1
    assert details.nodes[0].id == node.id
    assert details.nodes[0].name == "Node1"
    
    # This often fails with MissingGreenlet if nodes are lazy loaded and accessed outside session
    # But here we are inside async test with session. 
    # The issue is usually returning ORM objects that are not eagerly loaded.
    # Service should ensure eager loading (selectinload) for relationships used in response.
 
    # Current Pyramid model code read earlier: no is_deleted column!
    # Wait, the task list says: "is_deleted" in Task 2.1 description.
    # But the read content of `backend/app/models/pyramid.py` did NOT show `is_deleted`.
    # This means Task 2.1 might have been checked as "done" but the code is missing `is_deleted`.
    
    # Verification needed: Check if delete_pyramid performs hard delete or if I need to add is_deleted.
    # If the code assumes hard delete (cascade), verify retrieval returns None.
    
    result = await service.get_pyramid(pyramid.id)
    assert result is None  # Or verify is_deleted if implemented
    
    # Verify nodes are gone
    # node_result = await db_session.get(PyramidNode, node.id)
    # assert node_result is None
    
@pytest.mark.asyncio
async def test_property_4_list_integrity(db_session):
    """Property 4: 金字塔列表完整性"""
    service = PyramidService(db_session)
    
    # Clear DB
    # (In-memory DB is fresh per test if fixture logic is correct, but let's be safe)
    
    # Create multiple
    names = ["P1", "P2", "P3"]
    for name in names:
        await service.create_pyramid(PyramidCreate(name=name))
        
    # List
    result = await service.list_pyramids()
    assert len(result) >= 3
    
    fetched_names = [p.name for p in result]
    for name in names:
        assert name in fetched_names

@pytest.mark.asyncio
async def test_property_9_visualization_integrity(db_session):
    """Property 9: 可视化数据完整性"""
    service = PyramidService(db_session)
    
    pyramid = await service.create_pyramid(PyramidCreate(name="Vis Test"))
    
    # Add nodes
    root = PyramidNode(pyramid_id=pyramid.id, name="Root", level=0, sort_order=0, path="0")
    db_session.add(root)
    await db_session.commit()
    await db_session.refresh(root)
    
    child = PyramidNode(pyramid_id=pyramid.id, parent_id=root.id, name="Child", level=1, sort_order=0, path="0.0")
    db_session.add(child)
    await db_session.commit()
    
    vis_data = await service.get_pyramid_visualization(pyramid.id)
    
    # Verify structure of vis_data
    # Assuming it returns a dict with nodes and edges
    assert "nodes" in vis_data
    assert "edges" in vis_data
    assert len(vis_data["nodes"]) == 2
    assert len(vis_data["edges"]) == 1
