import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from app.models.content import ContentItem
from app.core.ai.facade import ai_facade
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
        quality_score = 50.0
        if item.validation_result and item.validation_result.overall_score is not None:
            quality_score = float(item.validation_result.overall_score)
            
        now = datetime.now(timezone.utc)
        created_at = item.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        age_days = (now - created_at).total_seconds() / 86400
        decay = math.exp(-age_days / 180.0)
        
        popularity = item.access_count or 0
        boost = 1.0 + (0.1 * math.log1p(popularity))
        
        final_score = quality_score * decay * boost
        
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
            stmt = select(ContentItem.id).where(
                ContentItem.lifecycle_status.in_(["ACTIVE", "DEPRECATED"])
            )
            result = await self.db.execute(stmt)
            all_ids = result.scalars().all()
            
            batch_size = 100
            for i in range(0, len(all_ids), batch_size):
                batch_ids = all_ids[i:i+batch_size]
                
                stmt = select(ContentItem).options(
                    selectinload(ContentItem.validation_result)
                ).where(ContentItem.id.in_(batch_ids))
                
                result = await self.db.execute(stmt)
                items = result.scalars().all()
                
                for item in items:
                    try:
                        stats["processed"] += 1
                        
                        new_score = self.calculate_score(item)
                        item.metabolism_score = new_score
                        
                        now = datetime.now(timezone.utc)
                        
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
                        
                        if item.lifecycle_status == "ACTIVE":
                            if new_score < 40.0 and age_days > 30:
                                item.lifecycle_status = "DEPRECATED"
                                stats["to_deprecated"] += 1
                                logger.info(f"Metabolism: Deprecated item {item.id} (Score: {new_score:.1f}, Age: {age_days:.1f}d)")

                        elif item.lifecycle_status == "DEPRECATED":
                            if age_days > 90 and inactive_days > 30:
                                item.lifecycle_status = "ARCHIVED"
                                stats["to_archived"] += 1
                                logger.info(f"Metabolism: Archived item {item.id} (Age: {age_days:.1f}d, Inactive: {inactive_days:.1f}d)")
                                
                    except Exception as e:
                        logger.error(f"Error processing item {item.id}: {e}")
                        continue
                
                await self.db.commit()

            return stats
            
        except Exception as e:
            logger.error(f"Fatal error in process_metabolism: {e}", exc_info=True)
            raise e

    async def get_cleanup_suggestions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取建议清理的内容列表。
        使用 AI 分析内容代谢状态，生成智能清理建议。
        """
        stmt = select(ContentItem).where(
            ContentItem.lifecycle_status == "ARCHIVED"
        ).order_by(ContentItem.metabolism_score.asc()).limit(limit)
        
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        if not items:
            logger.info("没有找到已归档的内容，无需清理建议")
            return []
        
        content_ids = [str(item.id) for item in items]
        
        try:
            logger.info(f"开始 AI 分析内容代谢状态，共 {len(content_ids)} 条内容")
            ai_result = await ai_facade.analyze_content_metabolism(content_ids, self.db)
            
            if ai_result.get("error"):
                logger.error(f"AI 分析内容代谢失败: {ai_result['error']}")
                return self._fallback_suggestions(items)
            
            suggestions = ai_result.get("suggestions", [])
            
            if not suggestions:
                logger.info("AI 分析未生成清理建议")
                return []
            
            formatted_suggestions = []
            for suggestion in suggestions:
                target_id = suggestion.get("target_id")
                if target_id:
                    item = next((i for i in items if str(i.id) == target_id), None)
                    if item:
                        formatted_suggestions.append({
                            "id": target_id,
                            "title": item.title,
                            "score": item.metabolism_score,
                            "age_days": (datetime.now(timezone.utc) - item.created_at).days if item.created_at else 0,
                            "reason": suggestion.get("reason", "AI 建议清理"),
                            "confidence": suggestion.get("confidence", 0.5),
                            "priority": suggestion.get("priority", "medium"),
                            "action_type": suggestion.get("action_type", "delete"),
                        })
            
            logger.info(f"AI 生成了 {len(formatted_suggestions)} 条清理建议")
            return formatted_suggestions
            
        except Exception as e:
            logger.error(f"获取清理建议时发生错误: {e}", exc_info=True)
            return self._fallback_suggestions(items)

    def _fallback_suggestions(self, items: List[ContentItem]) -> List[Dict[str, Any]]:
        """
        降级方案：当 AI 分析失败时，使用简单规则生成建议。
        """
        suggestions = []
        for item in items:
            if item.metabolism_score < 20.0:
                suggestions.append({
                    "id": str(item.id),
                    "title": item.title,
                    "score": item.metabolism_score,
                    "age_days": (datetime.now(timezone.utc) - item.created_at).days if item.created_at else 0,
                    "reason": f"低代谢分数 ({item.metabolism_score:.1f})",
                    "confidence": 0.6,
                    "priority": "low",
                    "action_type": "delete",
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
