import pytest
import uuid
import json
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.snapshot_service import SnapshotService

# Strategies
node_st = st.fixed_dictionaries({
    "id": st.uuids().map(str),
    "name": st.text(min_size=1),
    "description": st.text(),
    "level": st.integers(min_value=0, max_value=10),
    "sort_order": st.integers(min_value=0),
    "path": st.text(),
    "health_score": st.integers(min_value=0, max_value=100),
    "parent_id": st.one_of(st.none(), st.uuids().map(str))
})

snapshot_data_st = st.fixed_dictionaries({
    "pyramid": st.fixed_dictionaries({
        "id": st.uuids().map(str),
        "name": st.text(min_size=1),
        "description": st.text()
    }),
    "nodes": st.lists(node_st),
    "timestamp": st.text(), 
    "relations": st.lists(st.fixed_dictionaries({
        "id": st.uuids().map(str),
        "source_node_id": st.uuids().map(str),
        "target_node_id": st.uuids().map(str),
        "relation_type": st.text()
    }))
})

@pytest.mark.asyncio
async def test_validate_snapshot_data_valid_manual(db_session):
    service = SnapshotService(db_session)
    data = {
        "pyramid": {"id": str(uuid.uuid4()), "name": "test", "description": ""},
        "nodes": [],
        "timestamp": "2023-01-01",
        "relations": []
    }
    assert service._validate_snapshot_data(data) is True

@given(data=snapshot_data_st)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@pytest.mark.asyncio
async def test_validate_snapshot_data_properties(db_session, data):
    service = SnapshotService(db_session)
    # Our strategy generates valid structure, so it should pass
    assert service._validate_snapshot_data(data) is True

@given(data=st.dictionaries(keys=st.text(), values=st.text()))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@pytest.mark.asyncio
async def test_validate_snapshot_data_invalid(db_session, data):
    service = SnapshotService(db_session)
    # Random dictionaries are unlikely to have the exact required structure
    required = {"pyramid", "nodes", "timestamp"}
    if not required.issubset(data.keys()):
        assert service._validate_snapshot_data(data) is False
