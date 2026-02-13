import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, String
from sqlalchemy import String as sa_text_type
from app.models.hotspot import Hotspot, HotspotStatus
from app.models.content import ContentItem

logger = logging.getLogger(__name__)

class HotspotManager:
    """
    Manages the lifecycle of hotspots (emerging topics).
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_content_item(self, content: ContentItem):
        """
        Update hotspots based on a new content item.
        Assumes content.tags contains relevant topics.
        """
        if not content.tags:
            return

        tags = content.tags if isinstance(content.tags, list) else []
        
        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag = tag.strip()
            if not tag:
                continue
                
            # Check if hotspot exists
            result = await self.db.execute(
                select(Hotspot).where(Hotspot.topic_name == tag)
            )
            hotspot = result.scalars().first()
            
            now_utc = datetime.now(timezone.utc)
            
            if hotspot:
                hotspot.mention_count += 1
                hotspot.recent_7d_count += 1
                hotspot.last_mentioned_at = now_utc
                
                # Update related content IDs
                related_ids = list(hotspot.related_content_ids) if hotspot.related_content_ids else []
                content_id_str = str(content.id)
                if content_id_str not in related_ids:
                    related_ids.append(content_id_str)
                    # Keep only recent 50 for performance
                    if len(related_ids) > 50:
                        related_ids = related_ids[-50:]
                    hotspot.related_content_ids = related_ids
                    
            else:
                # Create new hotspot
                hotspot = Hotspot(
                    topic_name=tag,
                    status=HotspotStatus.EMERGING,
                    mention_count=1,
                    recent_7d_count=1,
                    previous_7d_count=0,
                    growth_rate=100.0, # Infinite growth essentially
                    related_content_ids=[str(content.id)],
                    first_seen_at=now_utc,
                    last_mentioned_at=now_utc,
                    status_changed_at=now_utc
                )
                self.db.add(hotspot)
        
        await self.db.commit()

    async def update_hotspot_stats(self):
        """
        Periodic task to update growth rates and statuses.
        """
        logger.info("Starting hotspot stats update...")
        
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)
        
        # Fetch all active hotspots
        result = await self.db.execute(
            select(Hotspot).where(Hotspot.status != HotspotStatus.ARCHIVED)
        )
        hotspots = result.scalars().all()
        
        for hotspot in hotspots:
            # Re-calculate counts from ContentItems
            # Note: This is an expensive operation (O(N*M)) where N=hotspots, M=content items in range.
            # In production, this should be optimized with search engine or aggregated tables.
            
            count_recent = await self._count_mentions(hotspot.topic_name, seven_days_ago, now)
            count_previous = await self._count_mentions(hotspot.topic_name, fourteen_days_ago, seven_days_ago)
            
            hotspot.recent_7d_count = count_recent
            hotspot.previous_7d_count = count_previous
            
            # Calculate growth rate
            if count_previous > 0:
                hotspot.growth_rate = ((count_recent - count_previous) / count_previous) * 100.0
            else:
                hotspot.growth_rate = 100.0 if count_recent > 0 else 0.0
                
            # Update Status
            self._update_status(hotspot, count_recent, now)
            
        await self.db.commit()
        logger.info("Hotspot stats update completed.")

    async def _count_mentions(self, topic: str, start_date: datetime, end_date: datetime) -> int:
        """
        Count mentions of a topic in content items within a date range.
        Uses a database-level JSON/text filter instead of loading all items into memory.
        For PostgreSQL this uses JSON containment; for SQLite it falls back to text LIKE.
        """
        from app.config import settings

        base_filter = [
            ContentItem.publish_time >= start_date,
            ContentItem.publish_time < end_date,
        ]

        if "postgresql" in settings.DATABASE_URL:
            # PostgreSQL: use JSON array containment operator via raw text
            from sqlalchemy import text, literal_column
            stmt = (
                select(func.count(ContentItem.id))
                .where(*base_filter)
                .where(ContentItem.tags.cast(sa_text_type).contains(f'"{topic}"'))
            )
        else:
            # SQLite / fallback: tags stored as JSON text, use LIKE
            stmt = (
                select(func.count(ContentItem.id))
                .where(*base_filter)
                .where(ContentItem.tags.cast(String).like(f'%"{topic}"%'))
            )

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    def _update_status(self, hotspot: Hotspot, recent_count: int, now: datetime):
        """
        Update hotspot status based on lifecycle rules.
        """
        # State Machine
        days_since_update = (now - hotspot.status_changed_at).days if hotspot.status_changed_at else 0
        days_since_seen = (now - hotspot.first_seen_at).days if hotspot.first_seen_at else 0
        days_inactive = (now - hotspot.last_mentioned_at).days if hotspot.last_mentioned_at else 0
        
        old_status = hotspot.status
        
        if hotspot.status == HotspotStatus.EMERGING:
            if recent_count > 10 and hotspot.growth_rate > 20:
                hotspot.status = HotspotStatus.TRENDING
            elif days_since_seen > 7 and recent_count < 5:
                 # If not trending after 7 days, cool down
                 hotspot.status = HotspotStatus.COOLING

        elif hotspot.status == HotspotStatus.TRENDING:
            if hotspot.growth_rate < -20 or recent_count < 5:
                hotspot.status = HotspotStatus.COOLING
            elif days_since_update > 30:
                 # Trending for too long -> Mature
                 hotspot.status = HotspotStatus.MATURE

        elif hotspot.status == HotspotStatus.MATURE:
            if recent_count < 3:
                hotspot.status = HotspotStatus.COOLING

        elif hotspot.status == HotspotStatus.COOLING:
            if days_inactive > 30:
                hotspot.status = HotspotStatus.ARCHIVED
            elif recent_count > 5 and hotspot.growth_rate > 20:
                # Revival
                hotspot.status = HotspotStatus.TRENDING
        
        if hotspot.status != old_status:
            hotspot.status_changed_at = now
            logger.info(f"Hotspot '{hotspot.topic_name}' changed status: {old_status} -> {hotspot.status}")
