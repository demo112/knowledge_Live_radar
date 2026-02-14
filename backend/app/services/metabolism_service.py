import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from app.models.content import ContentItem
import logging

logger = logging.getLogger(__name__)

class MetabolismService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def calculate_score(self, item: ContentItem) -> float:
        """
        Calculate metabolism score based on:
        1. Quality (from validation result or default)
        2. Age (time decay)
        3. Popularity (access count)
        """
        # 1. Base Quality Score (0-100)
        # If validated, use validation score. If not, assume 50 (neutral).
        quality_score = 50.0
        if item.validation_result and item.validation_result.overall_score is not None:
            quality_score = float(item.validation_result.overall_score)
            
        # 2. Time Decay
        # Half-life of 180 days (approx 6 months)
        now = datetime.now(timezone.utc)
        created_at = item.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        age_days = (now - created_at).total_seconds() / 86400
        decay = math.exp(-age_days / 180.0)
        
        # 3. Popularity Boost
        # Logarithmic boost: 0 views -> 1.0x, 10 views -> 1.24x, 100 views -> 1.46x
        popularity = item.access_count or 0
        boost = 1.0 + (0.1 * math.log1p(popularity))
        
        final_score = quality_score * decay * boost
        
        # Clamp between 0 and 100
        return min(100.0, max(0.0, final_score))

    async def process_metabolism(self) -> Dict[str, int]:
        """
        Execute daily metabolism batch job.
        1. Recalculate scores for all ACTIVE/DEPRECATED items.
        2. Transition ACTIVE -> DEPRECATED if score < 40 & age > 30 days.
        3. Transition DEPRECATED -> ARCHIVED if age > 90 days & inactive > 30 days.
        """
        stats = {
            "processed": 0,
            "to_deprecated": 0,
            "to_archived": 0
        }
        
        try:
            # Fetch all candidate IDs first to avoid pagination issues with changing status
            stmt = select(ContentItem.id).where(
                ContentItem.lifecycle_status.in_(["ACTIVE", "DEPRECATED"])
            )
            result = await self.db.execute(stmt)
            all_ids = result.scalars().all()
            
            batch_size = 100
            for i in range(0, len(all_ids), batch_size):
                batch_ids = all_ids[i:i+batch_size]
                
                # Eager load validation_result to avoid MissingGreenlet error
                stmt = select(ContentItem).options(
                    selectinload(ContentItem.validation_result)
                ).where(ContentItem.id.in_(batch_ids))
                
                result = await self.db.execute(stmt)
                items = result.scalars().all()
                
                for item in items:
                    try:
                        stats["processed"] += 1
                        
                        # 1. Update Score
                        new_score = self.calculate_score(item)
                        item.metabolism_score = new_score
                        
                        now = datetime.now(timezone.utc)
                        
                        # Ensure timezone awareness
                        created_at = item.created_at
                        if created_at and created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                            
                        age_days = (now - created_at).total_seconds() / 86400
                        
                        last_accessed = item.last_accessed_at
                        if last_accessed is None:
                            last_accessed = created_at
                        if last_accessed and last_accessed.tzinfo is None:
                            last_accessed = last_accessed.replace(tzinfo=timezone.utc)
                            
                        inactive_days = (now - last_accessed).total_seconds() / 86400
                        
                        # 2. Transition Logic
                        
                        # ACTIVE -> DEPRECATED
                        # Condition: Score < 40 AND Age > 30 days
                        if item.lifecycle_status == "ACTIVE":
                            if new_score < 40.0 and age_days > 30:
                                item.lifecycle_status = "DEPRECATED"
                                stats["to_deprecated"] += 1
                                logger.info(f"Metabolism: Deprecated item {item.id} (Score: {new_score:.1f}, Age: {age_days:.1f}d)")

                        # DEPRECATED -> ARCHIVED
                        # Condition: Age > 90 days AND Inactive > 30 days
                        elif item.lifecycle_status == "DEPRECATED":
                            if age_days > 90 and inactive_days > 30:
                                item.lifecycle_status = "ARCHIVED"
                                stats["to_archived"] += 1
                                logger.info(f"Metabolism: Archived item {item.id} (Age: {age_days:.1f}d, Inactive: {inactive_days:.1f}d)")
                                
                    except Exception as e:
                        logger.error(f"Error processing item {item.id}: {e}")
                        continue
                
                # Commit batch
                await self.db.commit()

            return stats
            
        except Exception as e:
            logger.error(f"Fatal error in process_metabolism: {e}", exc_info=True)
            raise e

    async def get_cleanup_suggestions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of items suggested for deletion (recycling bin).
        Criteria:
        1. Status is ARCHIVED
        2. Score < 20
        3. Age > 180 days
        """
        stmt = select(ContentItem).where(
            ContentItem.lifecycle_status == "ARCHIVED",
            ContentItem.metabolism_score < 20.0,
            ContentItem.created_at < datetime.now(timezone.utc) - timedelta(days=180)
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        suggestions = []
        for item in items:
            suggestions.append({
                "id": str(item.id),
                "title": item.title,
                "score": item.metabolism_score,
                "age_days": (datetime.now(timezone.utc) - item.created_at).days,
                "reason": f"Low score ({item.metabolism_score:.1f}) & Old age"
            })
            
        return suggestions

    async def execute_cleanup(self, item_ids: List[str]) -> int:
        """
        Soft delete (DELETED status) the specified items.
        """
        stmt = update(ContentItem).where(
            ContentItem.id.in_(item_ids)
        ).values(
            lifecycle_status="DELETED",
            is_deleted=True
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        count = result.rowcount
        logger.info(f"Metabolism: Soft deleted {count} items")
        return count
