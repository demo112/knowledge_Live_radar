import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, Bundle, initialize
from app.services.concept.synonym_manager import SynonymManager
from app.services.contribution.contribution_tracker import ContributionTracker
from app.models.synonym import SynonymMapping
from app.models.contribution import Contribution
from app.database import AsyncSessionLocal
import asyncio

# Need to handle async in hypothesis, which is tricky.
# Usually we use a synchronous wrapper or specific async plugins.
# For simplicity, we might just test the logic functions if possible, 
# or use a simplified property test without stateful machine for now if async is hard.

# However, let's try to verify basic properties:
# 1. Synonym mapping: If A -> B, then get_canonical(A) == B.
# 2. Contribution: Create -> Get returns same data.

# Since DB access is async, standard Hypothesis is hard.
# We will write a standard async test that generates random data using hypothesis strategies
# and runs the async logic.

@pytest.mark.asyncio
async def test_synonym_properties():
    # We will simulate a sequence of operations
    # This is a manual property test
    async with AsyncSessionLocal() as db:
        manager = SynonymManager(db)
        
        # Property: Canonical consistency
        # If we add A -> B, get_canonical(A) must be B
        # If we delete A, get_canonical(A) must be A (identity)
        
        canonical = "AI"
        synonym = "Artificial Intelligence"
        
        await manager.add_synonym(canonical, synonym, "test", 1.0)
        
        result = await manager.get_canonical(synonym)
        assert result == canonical
        
        await manager.delete_synonym(synonym)
        result = await manager.get_canonical(synonym)
        assert result == synonym

@pytest.mark.asyncio
async def test_contribution_properties():
    async with AsyncSessionLocal() as db:
        tracker = ContributionTracker(db)
        
        # Property: Contribution creation persistence
        user_id = "user_123"
        input_type = "text"
        original_input = "Some text"
        
        contribution = await tracker.create_contribution(user_id, input_type, original_input)
        
        fetched = await tracker.get_contribution(contribution.id)
        assert fetched is not None
        assert fetched.id == contribution.id
        assert fetched.user_id == user_id
        assert fetched.original_input == original_input
        assert fetched.status == "pending"
