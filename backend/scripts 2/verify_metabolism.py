import asyncio
import sys
import os
import math
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.content import ContentItem, ValidationResult
from app.services.metabolism_service import MetabolismService

async def main():
    print("Starting metabolism verification...")
    
    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # 1. Create test data
        now = datetime.now(timezone.utc)
        
        # Case 1: Should become DEPRECATED
        # Criteria: score < 40 AND age > 30 days
        # Age = 40 days -> Decay = exp(-40/180) = 0.8007
        # Quality = 40 -> Score = 40 * 0.8007 = 32.02
        item1_id = uuid4()
        item1 = ContentItem(
            id=item1_id,
            title="Test Item 1 (To Deprecate)",
            url=f"http://test.com/{item1_id}",
            lifecycle_status="ACTIVE",
            created_at=now - timedelta(days=40),
            last_accessed_at=now - timedelta(days=40),
            access_count=0
        )
        val1 = ValidationResult(content_id=item1_id, overall_score=40)
        
        # Case 2: Should become ARCHIVED
        # Criteria: status == DEPRECATED AND age > 90 days AND inactive > 30 days
        item2_id = uuid4()
        item2 = ContentItem(
            id=item2_id,
            title="Test Item 2 (To Archive)",
            url=f"http://test.com/{item2_id}",
            lifecycle_status="DEPRECATED",
            created_at=now - timedelta(days=100),
            last_accessed_at=now - timedelta(days=40),
            access_count=0
        )
        # Score doesn't matter for this transition, but let's give it one
        val2 = ValidationResult(content_id=item2_id, overall_score=30)
        
        # Case 3: Should stay ACTIVE
        # Criteria: score > 40 OR age < 30 days
        # Age = 40 days -> Decay = 0.8
        # Quality = 80 -> Score = 80 * 0.8 = 64
        # Popularity = 100 -> Boost = 1 + 0.1 * ln(101) = 1.46
        # Final Score = 64 * 1.46 = 93.44
        item3_id = uuid4()
        item3 = ContentItem(
            id=item3_id,
            title="Test Item 3 (Stay Active)",
            url=f"http://test.com/{item3_id}",
            lifecycle_status="ACTIVE",
            created_at=now - timedelta(days=40),
            last_accessed_at=now,
            access_count=100
        )
        val3 = ValidationResult(content_id=item3_id, overall_score=80)

        session.add_all([item1, val1, item2, val2, item3, val3])
        await session.commit()
        print(f"Created test items: \n  1. {item1_id}\n  2. {item2_id}\n  3. {item3_id}")
        
        # 2. Run metabolism service
        print("Running metabolism service...")
        service = MetabolismService(session)
        stats = await service.process_metabolism()
        print(f"Metabolism run stats: {stats}")
        
        # 3. Verify results
        # Refresh items
        result1 = await session.execute(select(ContentItem).where(ContentItem.id == item1_id))
        item1_updated = result1.scalar_one()
        
        result2 = await session.execute(select(ContentItem).where(ContentItem.id == item2_id))
        item2_updated = result2.scalar_one()
        
        result3 = await session.execute(select(ContentItem).where(ContentItem.id == item3_id))
        item3_updated = result3.scalar_one()
        
        print("\nVerification Results:")
        print(f"Item 1 (Expect DEPRECATED): {item1_updated.lifecycle_status} (Score: {item1_updated.metabolism_score:.2f})")
        print(f"Item 2 (Expect ARCHIVED): {item2_updated.lifecycle_status}")
        print(f"Item 3 (Expect ACTIVE): {item3_updated.lifecycle_status} (Score: {item3_updated.metabolism_score:.2f})")
        
        success = True
        if item1_updated.lifecycle_status != "DEPRECATED":
            print("❌ Item 1 failed")
            success = False
        if item2_updated.lifecycle_status != "ARCHIVED":
            print("❌ Item 2 failed")
            success = False
        if item3_updated.lifecycle_status != "ACTIVE":
            print("❌ Item 3 failed")
            success = False
            
        if success:
            print("\n✅ All verifications passed!")
            
        # Cleanup
        await session.delete(val1)
        await session.delete(val2)
        await session.delete(val3)
        await session.delete(item1_updated)
        await session.delete(item2_updated)
        await session.delete(item3_updated)
        await session.commit()
        print("Cleanup done.")

if __name__ == "__main__":
    asyncio.run(main())
