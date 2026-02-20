import logging
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader
from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource
from app.models.content import ContentItem, ContentNodeRelation
from app.models.ai_suggestion import AISuggestion

logger = logging.getLogger(__name__)


class SuggestionProcessor:
    """AI 建议生成处理器"""

    async def analyze_pyramid_health(
        self,
        pyramid_id: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        分析金字塔健康状态并生成建议

        Args:
            pyramid_id: 金字塔 ID
            db: 数据库会话（可选）

        Returns:
            包含分析和建议的字典
        """
        should_close_db = db is None
        db = db or AsyncSessionLocal()

        try:
            pyramid_uuid = uuid.UUID(pyramid_id)
            data = await self._collect_pyramid_data(pyramid_uuid, db)

            if not data.get("pyramid"):
                logger.error(f"金字塔不存在: {pyramid_id}")
                return {"error": "金字塔不存在", "suggestions": []}

            prompt_content, metadata = prompt_loader.render_prompt(
                "pyramid/health_analysis",
                {
                    "pyramid_structure": data["structure"],
                    "node_stats": data["node_stats"],
                    "content_stats": data["content_stats"],
                    "activity_stats": data["activity_stats"],
                }
            )

            if not prompt_content:
                raise ValueError("无法加载金字塔健康分析 Prompt")

            model = metadata.get("model") if metadata else None
            messages = [{"role": "user", "content": prompt_content}]

            logger.info(f"开始分析金字塔健康状态: {pyramid_id}")
            response_text = await ai_client.chat_completion(messages, model=model, context="pyramid_health")

            if not response_text:
                raise ValueError("AI 返回空响应")

            result = ai_client.parse_json(response_text)

            if not result:
                logger.error(f"无法解析 AI 响应: {response_text[:200]}")
                return {"error": "无法解析 AI 响应", "suggestions": []}

            suggestions = result.get("suggestions", [])
            stored_ids = await self._store_suggestions(
                suggestions,
                pyramid_id=pyramid_id,
                db=db
            )

            return {
                "analysis": result.get("analysis", {}),
                "suggestions": suggestions,
                "suggestion_ids": stored_ids,
            }

        except Exception as e:
            logger.error(f"分析金字塔健康状态失败: {e}")
            return {"error": str(e), "suggestions": []}
        finally:
            if should_close_db:
                await db.close()

    async def analyze_source_health(
        self,
        source_id: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        分析信息源健康状态并生成建议

        Args:
            source_id: 信息源 ID
            db: 数据库会话（可选）

        Returns:
            包含分析和建议的字典
        """
        should_close_db = db is None
        db = db or AsyncSessionLocal()

        try:
            source_uuid = uuid.UUID(source_id)
            data = await self._collect_source_data(source_uuid, db)

            if not data.get("source"):
                logger.error(f"信息源不存在: {source_id}")
                return {"error": "信息源不存在", "suggestions": []}

            prompt_content, metadata = prompt_loader.render_prompt(
                "source/health_analysis",
                {
                    "source_info": data["source_info"],
                    "crawl_history": data["crawl_history"],
                    "error_stats": data["error_stats"],
                    "content_quality": data["content_quality"],
                }
            )

            if not prompt_content:
                raise ValueError("无法加载信息源健康分析 Prompt")

            model = metadata.get("model") if metadata else None
            messages = [{"role": "user", "content": prompt_content}]

            logger.info(f"开始分析信息源健康状态: {source_id}")
            response_text = await ai_client.chat_completion(messages, model=model, context="source_health")

            if not response_text:
                raise ValueError("AI 返回空响应")

            result = ai_client.parse_json(response_text)

            if not result:
                logger.error(f"无法解析 AI 响应: {response_text[:200]}")
                return {"error": "无法解析 AI 响应", "suggestions": []}

            suggestions = result.get("suggestions", [])
            stored_ids = await self._store_suggestions(
                suggestions,
                source_id=source_id,
                db=db
            )

            return {
                "analysis": result.get("analysis", {}),
                "suggestions": suggestions,
                "suggestion_ids": stored_ids,
            }

        except Exception as e:
            logger.error(f"分析信息源健康状态失败: {e}")
            return {"error": str(e), "suggestions": []}
        finally:
            if should_close_db:
                await db.close()

    async def analyze_content_metabolism(
        self,
        content_ids: List[str],
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        分析内容代谢状态并生成建议

        Args:
            content_ids: 内容 ID 列表
            db: 数据库会话（可选）

        Returns:
            包含分析和建议的字典
        """
        should_close_db = db is None
        db = db or AsyncSessionLocal()

        try:
            content_uuids = [uuid.UUID(cid) for cid in content_ids]
            data = await self._collect_content_data(content_uuids, db)

            prompt_content, metadata = prompt_loader.render_prompt(
                "analysis/metabolism",
                {
                    "content_list": data["content_list"],
                    "quality_scores": data["quality_scores"],
                }
            )

            if not prompt_content:
                raise ValueError("无法加载内容代谢分析 Prompt")

            model = metadata.get("model") if metadata else None
            messages = [{"role": "user", "content": prompt_content}]

            logger.info(f"开始分析内容代谢状态: {len(content_ids)} 条内容")
            response_text = await ai_client.chat_completion(messages, model=model, context="content_metabolism")

            if not response_text:
                raise ValueError("AI 返回空响应")

            result = ai_client.parse_json(response_text)

            if not result:
                logger.error(f"无法解析 AI 响应: {response_text[:200]}")
                return {"error": "无法解析 AI 响应", "suggestions": []}

            suggestions = result.get("suggestions", [])
            stored_ids = await self._store_suggestions(suggestions, db=db)

            return {
                "analysis": result.get("analysis", {}),
                "suggestions": suggestions,
                "suggestion_ids": stored_ids,
            }

        except Exception as e:
            logger.error(f"分析内容代谢状态失败: {e}")
            return {"error": str(e), "suggestions": []}
        finally:
            if should_close_db:
                await db.close()

    async def analyze_concept_drift(
        self,
        node_id: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        分析概念漂移并生成建议

        Args:
            node_id: 节点 ID
            db: 数据库会话（可选）

        Returns:
            包含分析和建议的字典
        """
        should_close_db = db is None
        db = db or AsyncSessionLocal()

        try:
            node_uuid = uuid.UUID(node_id)
            data = await self._collect_node_data(node_uuid, db)

            if not data.get("node"):
                logger.error(f"节点不存在: {node_id}")
                return {"error": "节点不存在", "suggestions": []}

            prompt_content, metadata = prompt_loader.render_prompt(
                "analysis/drift_detection",
                {
                    "concept_name": data["concept_name"],
                    "concept_description": data["concept_description"],
                    "old_content": data["old_content"],
                    "new_content": data["new_content"],
                    "old_days": data["old_days"],
                    "new_days": data["new_days"],
                }
            )

            if not prompt_content:
                raise ValueError("无法加载漂移检测 Prompt")

            model = metadata.get("model") if metadata else None
            messages = [{"role": "user", "content": prompt_content}]

            logger.info(f"开始分析概念漂移: {node_id}")
            response_text = await ai_client.chat_completion(messages, model=model, context="drift_detection")

            if not response_text:
                raise ValueError("AI 返回空响应")

            drift_result = self._parse_drift_response(response_text)

            suggestions = []
            if drift_result.get("has_drift"):
                suggestions.append({
                    "action_type": "update_node",
                    "target_id": node_id,
                    "target_name": data["concept_name"],
                    "reason": f"检测到概念漂移: {drift_result.get('reason', '语义发生显著变化')}",
                    "params": {
                        "description": "建议更新节点描述以反映概念演变",
                    },
                    "confidence": 0.8,
                    "priority": "medium"
                })

            stored_ids = await self._store_suggestions(
                suggestions,
                pyramid_id=str(data.get("pyramid_id")),
                db=db
            )

            return {
                "analysis": drift_result,
                "suggestions": suggestions,
                "suggestion_ids": stored_ids,
            }

        except Exception as e:
            logger.error(f"分析概念漂移失败: {e}")
            return {"error": str(e), "suggestions": []}
        finally:
            if should_close_db:
                await db.close()

    async def _collect_pyramid_data(
        self,
        pyramid_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """收集金字塔数据"""
        result = await db.execute(
            select(Pyramid).where(Pyramid.id == pyramid_id, Pyramid.is_deleted == False)
        )
        pyramid = result.scalar_one_or_none()

        if not pyramid:
            return {"pyramid": None}

        nodes_result = await db.execute(
            select(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id, PyramidNode.is_deleted == False)
            .order_by(PyramidNode.level, PyramidNode.sort_order)
        )
        nodes = nodes_result.scalars().all()

        structure = self._build_node_tree(nodes)

        node_stats = {
            "total_count": len(nodes),
            "level_distribution": {},
            "empty_nodes": [],
            "low_health_nodes": [],
        }

        for node in nodes:
            level = node.level
            node_stats["level_distribution"][level] = node_stats["level_distribution"].get(level, 0) + 1

            if node.content_count == 0:
                node_stats["empty_nodes"].append({
                    "id": str(node.id),
                    "name": node.name,
                    "level": node.level,
                })

            if node.health_score < 60:
                node_stats["low_health_nodes"].append({
                    "id": str(node.id),
                    "name": node.name,
                    "health_score": node.health_score,
                })

        content_stats = await self._get_content_stats(pyramid_id, db)

        activity_stats = {
            "last_content_at": None,
            "content_trend": "stable",
        }

        recent_content = await db.execute(
            select(ContentItem)
            .join(ContentNodeRelation, ContentItem.id == ContentNodeRelation.content_id)
            .join(PyramidNode, ContentNodeRelation.node_id == PyramidNode.id)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .order_by(ContentItem.created_at.desc())
            .limit(1)
        )
        recent = recent_content.scalar_one_or_none()
        if recent:
            activity_stats["last_content_at"] = recent.created_at.isoformat()

        return {
            "pyramid": pyramid,
            "structure": json.dumps(structure, ensure_ascii=False, indent=2),
            "node_stats": json.dumps(node_stats, ensure_ascii=False, indent=2),
            "content_stats": json.dumps(content_stats, ensure_ascii=False, indent=2),
            "activity_stats": json.dumps(activity_stats, ensure_ascii=False, indent=2),
        }

    async def _collect_source_data(
        self,
        source_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """收集信息源数据"""
        result = await db.execute(
            select(InformationSource).where(
                InformationSource.id == source_id,
                InformationSource.is_deleted == False
            )
        )
        source = result.scalar_one_or_none()

        if not source:
            return {"source": None}

        source_info = {
            "id": str(source.id),
            "name": source.name,
            "type": source.type,
            "url": source.url,
            "status": source.status,
            "health_score": source.health_score,
            "check_interval": source.check_interval,
            "created_at": source.created_at.isoformat() if source.created_at else None,
        }

        crawl_history = {
            "last_crawled_at": source.last_crawled_at.isoformat() if source.last_crawled_at else None,
            "trial_runs": source.trial_runs,
            "trial_successes": source.trial_successes,
            "success_rate": source.trial_successes / source.trial_runs if source.trial_runs > 0 else 0,
        }

        error_stats = {
            "error_count": source.error_count,
            "recovery_count": source.recovery_count,
            "last_error_message": source.last_error_message,
        }

        content_quality = await self._get_source_content_quality(source_id, db)

        return {
            "source": source,
            "source_info": json.dumps(source_info, ensure_ascii=False, indent=2),
            "crawl_history": json.dumps(crawl_history, ensure_ascii=False, indent=2),
            "error_stats": json.dumps(error_stats, ensure_ascii=False, indent=2),
            "content_quality": json.dumps(content_quality, ensure_ascii=False, indent=2),
        }

    async def _collect_content_data(
        self,
        content_ids: List[uuid.UUID],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """收集内容数据"""
        result = await db.execute(
            select(ContentItem).where(ContentItem.id.in_(content_ids))
        )
        contents = result.scalars().all()

        content_items = []

        for content in contents:
            content_items.append({
                "id": str(content.id),
                "title": content.title,
                "lifecycle_status": content.lifecycle_status,
                "metabolism_score": content.metabolism_score,
                "access_count": content.access_count,
                "last_accessed_at": content.last_accessed_at.isoformat() if content.last_accessed_at else None,
                "created_at": content.created_at.isoformat() if content.created_at else None,
            })

        quality_scores = {
            "avg_metabolism_score": sum(c.metabolism_score for c in contents) / len(contents) if contents else 0,
            "low_quality_count": sum(1 for c in contents if c.metabolism_score < 40),
            "stale_count": sum(1 for c in contents if c.access_count == 0 and c.metabolism_score < 60),
        }

        return {
            "content_list": json.dumps(content_items, ensure_ascii=False, indent=2),
            "quality_scores": json.dumps(quality_scores, ensure_ascii=False, indent=2),
        }

    async def _collect_node_data(
        self,
        node_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """收集节点数据"""
        result = await db.execute(
            select(PyramidNode).where(PyramidNode.id == node_id, PyramidNode.is_deleted == False)
        )
        node = result.scalar_one_or_none()

        if not node:
            return {"node": None}

        now = datetime.utcnow()
        old_threshold = now - timedelta(days=30)
        new_threshold = now - timedelta(days=7)

        old_contents_result = await db.execute(
            select(ContentItem)
            .join(ContentNodeRelation, ContentItem.id == ContentNodeRelation.content_id)
            .where(
                ContentNodeRelation.node_id == node_id,
                ContentItem.created_at < old_threshold
            )
            .order_by(ContentItem.created_at.desc())
            .limit(10)
        )
        old_contents = old_contents_result.scalars().all()

        new_contents_result = await db.execute(
            select(ContentItem)
            .join(ContentNodeRelation, ContentItem.id == ContentNodeRelation.content_id)
            .where(
                ContentNodeRelation.node_id == node_id,
                ContentItem.created_at >= new_threshold
            )
            .order_by(ContentItem.created_at.desc())
            .limit(10)
        )
        new_contents = new_contents_result.scalars().all()

        old_content_text = "\n".join([
            f"- {c.title}: {(c.summary or c.content_text or '')[:200]}"
            for c in old_contents
        ]) or "无历史内容"

        new_content_text = "\n".join([
            f"- {c.title}: {(c.summary or c.content_text or '')[:200]}"
            for c in new_contents
        ]) or "无近期内容"

        return {
            "node": node,
            "pyramid_id": node.pyramid_id,
            "concept_name": node.name,
            "concept_description": node.description or "无描述",
            "old_content": old_content_text,
            "new_content": new_content_text,
            "old_days": 30,
            "new_days": 7,
        }

    def _build_node_tree(self, nodes: List[PyramidNode]) -> Dict[str, Any]:
        """构建节点树结构"""
        node_map = {str(n.id): {"id": str(n.id), "name": n.name, "level": n.level, "children": []} for n in nodes}
        root_nodes = []

        for node in nodes:
            node_data = node_map[str(node.id)]
            if node.parent_id:
                parent_id = str(node.parent_id)
                if parent_id in node_map:
                    node_map[parent_id]["children"].append(node_data)
            else:
                root_nodes.append(node_data)

        return root_nodes

    async def _get_content_stats(
        self,
        pyramid_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取金字塔内容统计"""
        total_result = await db.execute(
            select(func.count(ContentItem.id.distinct()))
            .join(ContentNodeRelation, ContentItem.id == ContentNodeRelation.content_id)
            .join(PyramidNode, ContentNodeRelation.node_id == PyramidNode.id)
            .where(PyramidNode.pyramid_id == pyramid_id)
        )
        total_count = total_result.scalar() or 0

        status_result = await db.execute(
            select(ContentItem.status, func.count(ContentItem.id))
            .join(ContentNodeRelation, ContentItem.id == ContentNodeRelation.content_id)
            .join(PyramidNode, ContentNodeRelation.node_id == PyramidNode.id)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .group_by(ContentItem.status)
        )
        status_counts = {row[0]: row[1] for row in status_result.all()}

        return {
            "total_count": total_count,
            "status_distribution": status_counts,
        }

    async def _get_source_content_quality(
        self,
        source_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取信息源内容质量统计"""
        total_result = await db.execute(
            select(func.count(ContentItem.id))
            .where(ContentItem.source_id == source_id)
        )
        total_count = total_result.scalar() or 0

        avg_score_result = await db.execute(
            select(func.avg(ContentItem.metabolism_score))
            .where(ContentItem.source_id == source_id)
        )
        avg_score = avg_score_result.scalar() or 0

        return {
            "total_count": total_count,
            "avg_metabolism_score": round(avg_score, 2),
        }

    def _parse_drift_response(self, response: str) -> Dict[str, Any]:
        """解析漂移检测响应"""
        response_upper = response.upper()
        has_drift = "YES:" in response_upper or response_upper.startswith("YES")

        reason = ""
        if "理由:" in response or "理由：" in response:
            parts = response.split("理由:") if "理由:" in response else response.split("理由：")
            if len(parts) > 1:
                reason = parts[1].strip()

        return {
            "has_drift": has_drift,
            "reason": reason,
            "raw_response": response,
        }

    def _parse_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """解析 AI 响应中的建议"""
        result = ai_client.parse_json(response)
        return result.get("suggestions", [])

    async def _store_suggestions(
        self,
        suggestions: List[Dict[str, Any]],
        pyramid_id: str = None,
        source_id: str = None,
        db: AsyncSession = None
    ) -> List[str]:
        """存储建议到数据库"""
        if not suggestions:
            return []

        should_close_db = db is None
        db = db or AsyncSessionLocal()
        stored_ids = []

        try:
            for suggestion_data in suggestions:
                input_hash = hashlib.sha256(
                    json.dumps(suggestion_data, sort_keys=True, ensure_ascii=False).encode()
                ).hexdigest()

                suggestion = AISuggestion(
                    type="health_analysis",
                    input_hash=input_hash,
                    data=suggestion_data.get("params", {}),
                    confidence=suggestion_data.get("confidence"),
                    action_type=suggestion_data.get("action_type", "update_node"),
                    target_type="pyramid_node" if pyramid_id else "information_source",
                    target_id=uuid.UUID(suggestion_data["target_id"]) if suggestion_data.get("target_id") else None,
                    target_name=suggestion_data.get("target_name"),
                    reason=suggestion_data.get("reason", ""),
                    params=suggestion_data.get("params", {}),
                    status="pending",
                    pyramid_id=uuid.UUID(pyramid_id) if pyramid_id else None,
                    source_id=uuid.UUID(source_id) if source_id else None,
                )

                db.add(suggestion)
                stored_ids.append(str(suggestion.id))

            await db.commit()
            logger.info(f"已存储 {len(stored_ids)} 条建议")

        except Exception as e:
            logger.error(f"存储建议失败: {e}")
            await db.rollback()
        finally:
            if should_close_db:
                await db.close()

        return stored_ids


suggestion_processor = SuggestionProcessor()
