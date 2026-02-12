import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.services.impact_analyzer import ImpactAnalyzer
from app.models.approval import Approval
from app.models.pyramid import PyramidNode

@pytest.mark.asyncio
async def test_analyze_create_node():
    db = AsyncMock()
    analyzer = ImpactAnalyzer(db)
    
    approval = Approval(type="create_node", target_id=None)
    impact = await analyzer.analyze_impact(approval)
    
    assert impact["risk_level"] == "low"
    assert impact["affected_nodes_count"] == 0

@pytest.mark.asyncio
async def test_analyze_update_node():
    db = AsyncMock()
    analyzer = ImpactAnalyzer(db)
    
    node_id = uuid.uuid4()
    # Fix: use name instead of title
    node = PyramidNode(id=node_id, name="Test Node")
    
    # Mock _get_node by mocking db.execute
    # This is complex because of sqlalchemy's async execution pattern.
    # Easier to mock the _get_node method directly for unit testing logic.
    analyzer._get_node = AsyncMock(return_value=node)
    
    approval = Approval(type="update_node", target_id=node_id)
    impact = await analyzer.analyze_impact(approval)
    
    assert impact["risk_level"] == "medium"
    assert impact["affected_nodes_count"] == 1
    # Fix: check title -> name mapping logic in ImpactAnalyzer or update test expectation
    # ImpactAnalyzer uses node.title, but model has node.name. 
    # Wait, ImpactAnalyzer code used node.title! I need to fix ImpactAnalyzer code too.
    assert impact["affected_nodes"][0]["id"] == str(node.id)
