import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pyramid import PyramidNode
from app.models.ai_suggestion import AISuggestion
from app.core.ai.facade import ai_facade

logger = logging.getLogger(__name__)


class RestructureAdvisor:
    """
    金字塔结构分析与重构建议生成器。
    
    通过 AI 分析金字塔健康状态，生成结构优化建议。
    阈值作为上下文参考传递给 AI，由 AI 综合判断是否需要调整。
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_and_propose(self, pyramid_id: uuid.UUID) -> List[AISuggestion]:
        """
        分析金字塔结构并生成重构提案。
        
        Args:
            pyramid_id: 金字塔 ID
            
        Returns:
            生成的 AI 建议列表
        """
        logger.info(f"开始分析金字塔结构: {pyramid_id}")
        
        result = await ai_facade.analyze_pyramid_health(str(pyramid_id), self.db)
        
        if result.get("error"):
            logger.error(f"AI 分析失败: {result['error']}")
            return []
        
        suggestions = result.get("suggestions", [])
        if not suggestions:
            logger.info(f"金字塔 {pyramid_id} 无需结构调整")
            return []
        
        existing_suggestions = await self._fetch_pending_structure_suggestions(pyramid_id)
        existing_keys = set((s.action_type, s.target_id) for s in existing_suggestions)
        
        saved_suggestions = []
        for suggestion in suggestions:
            ai_suggestion = self._suggestion_to_ai_suggestion(suggestion, pyramid_id)
            if ai_suggestion and (ai_suggestion.action_type, ai_suggestion.target_id) not in existing_keys:
                self.db.add(ai_suggestion)
                saved_suggestions.append(ai_suggestion)
        
        if saved_suggestions:
            await self.db.commit()
            for s in saved_suggestions:
                await self.db.refresh(s)
            logger.info(f"生成了 {len(saved_suggestions)} 条重构建议")
        else:
            logger.info("无新增重构建议")
            
        return saved_suggestions

    async def _fetch_pending_structure_suggestions(self, pyramid_id: uuid.UUID) -> List[AISuggestion]:
        """获取金字塔的待处理结构建议"""
        action_types = ["split_node", "move_node", "merge_node", "create_node", "delete_node", "update_node"]
        
        # Directly query by pyramid_id if available in AISuggestion (it is)
        stmt = (
            select(AISuggestion)
            .where(AISuggestion.status == "pending")
            .where(AISuggestion.action_type.in_(action_types))
            .where(AISuggestion.pyramid_id == pyramid_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _suggestion_to_ai_suggestion(self, suggestion: Dict[str, Any], pyramid_id: uuid.UUID) -> Optional[AISuggestion]:
        """
        将 AI 建议转换为 AISuggestion 对象。
        
        Args:
            suggestion: AI 返回的建议字典
            pyramid_id: 金字塔 ID
            
        Returns:
            AISuggestion 对象，如果转换失败则返回 None
        """
        action_type = suggestion.get("action_type", "")
        target_id_str = suggestion.get("target_id")
        
        if not target_id_str:
            # Some actions like create_node might not have target_id yet if it's new
            # But usually they refer to parent_id or something.
            # Let's assume target_id is required for existing nodes.
            if action_type != "create_node":
                logger.warning(f"建议缺少 target_id: {suggestion}")
                return None
        
        target_id = None
        if target_id_str:
            try:
                target_id = uuid.UUID(target_id_str)
            except ValueError:
                logger.warning(f"无效的 target_id: {target_id_str}")
                return None
        
        type_mapping = {
            "split_node": "split_node",
            "merge_node": "merge_node",
            "move_node": "move_node",
            "update_node": "update_node",
            "create_node": "create_node",
            "delete_node": "delete_node",
        }
        
        mapped_action_type = type_mapping.get(action_type, action_type)
        
        # Ensure params is a dict
        params = suggestion.get("params", {})
        if not isinstance(params, dict):
            params = {}
            
        # Inject pyramid_id into params if not present
        if "pyramid_id" not in params:
            params["pyramid_id"] = str(pyramid_id)
            
        return AISuggestion(
            type="structure_optimization",
            action_type=mapped_action_type,
            target_type="pyramid_node",
            target_id=target_id,
            target_name=suggestion.get("target_name"),
            pyramid_id=pyramid_id,
            status="pending",
            confidence=suggestion.get("confidence", 0.7),
            reason=suggestion.get("reason", ""),
            params=params,
            data=suggestion,  # Store full raw suggestion in data
            input_hash=str(uuid.uuid4())[:8] # Simple hash for now
        )
