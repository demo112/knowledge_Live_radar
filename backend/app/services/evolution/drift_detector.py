import uuid
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pyramid import PyramidNode
from app.models.ai_suggestion import AISuggestion
from app.core.ai.facade import ai_facade

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    通过比较历史内容和近期内容来检测知识概念（节点）的语义漂移。
    使用模板化的 AI 分析生成漂移检测建议。
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_drift(self, pyramid_id: uuid.UUID) -> List[AISuggestion]:
        """
        扫描金字塔中所有节点的概念漂移。
        使用 ai_facade.analyze_concept_drift 进行模板化分析。
        """
        logger.info(f"开始检测金字塔 {pyramid_id} 的概念漂移")
        suggestions = []

        nodes = await self._fetch_nodes(pyramid_id)

        for node in nodes:
            drift = await self._check_node_drift(node)
            if drift:
                suggestions.append(drift)

        saved_suggestions = []
        for s in suggestions:
            exists = await self._drift_suggestion_exists(s.target_id)
            if not exists:
                self.db.add(s)
                saved_suggestions.append(s)

        if saved_suggestions:
            await self.db.commit()
            for s in saved_suggestions:
                await self.db.refresh(s)
            logger.info(f"检测到 {len(saved_suggestions)} 个概念存在漂移")

        return saved_suggestions

    async def _check_node_drift(self, node: PyramidNode) -> Optional[AISuggestion]:
        try:
            drift_result = await ai_facade.analyze_concept_drift(
                node_id=str(node.id),
                db=self.db
            )

            if drift_result.get("error"):
                logger.warning(f"节点 {node.id} 漂移分析失败: {drift_result.get('error')}")
                return None

            analysis = drift_result.get("analysis", {})
            suggestions = drift_result.get("suggestions", [])

            if not analysis.get("drift_detected"):
                return None

            drift_type = analysis.get("drift_type", "unknown")
            drift_score = analysis.get("drift_score", 0.0)
            drift_details = analysis.get("drift_details", "")
            evidence = analysis.get("evidence", [])

            action_type = "fix_drift"
            params = {}
            if suggestions:
                first_suggestion = suggestions[0]
                action_type = first_suggestion.get("action_type", "fix_drift")
                params = first_suggestion.get("params", {})
            
            # Inject pyramid_id and node_id into params if not present
            if "pyramid_id" not in params:
                params["pyramid_id"] = str(node.pyramid_id)
            if "node_id" not in params:
                params["node_id"] = str(node.id)

            return AISuggestion(
                type="concept_drift",
                action_type=action_type,
                target_type="pyramid_node",
                target_id=node.id,
                target_name=node.name,
                pyramid_id=node.pyramid_id,
                status="pending",
                confidence=drift_score,
                reason=f"概念漂移检测: {drift_details}",
                params=params,
                data={
                    "drift_type": drift_type,
                    "drift_score": drift_score,
                    "drift_details": drift_details,
                    "evidence": evidence,
                    "suggestions": suggestions,
                    "suggestion_ids": drift_result.get("suggestion_ids", []),
                },
                input_hash=str(uuid.uuid4())[:8] # Simple hash for now
            )
        except Exception as e:
            logger.error(f"检测节点 {node.id} 漂移时出错: {e}")
            return None

    async def _fetch_nodes(self, pyramid_id: uuid.UUID) -> List[PyramidNode]:
        result = await self.db.execute(
            select(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .where(PyramidNode.is_deleted == False)
        )
        return result.scalars().all()

    async def _drift_suggestion_exists(self, node_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(AISuggestion)
            .where(AISuggestion.type == "concept_drift")
            .where(AISuggestion.target_id == node_id)
            .where(AISuggestion.status == "pending")
        )
        return result.scalars().first() is not None
