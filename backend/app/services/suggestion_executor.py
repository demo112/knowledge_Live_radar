import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_suggestion import AISuggestion
from app.models.pyramid import PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.source import InformationSource, SourceNodeRelation
from app.services.snapshot_service import SnapshotService
from app.schemas.pyramid import (
    PyramidNodeCreate, 
    PyramidNodeUpdate, 
    NodeSplitRequest, 
    NodeMergeRequest
)

logger = logging.getLogger(__name__)


class SuggestionExecutor:
    """AI 建议执行器

    负责解析 AI 建议并执行对应的操作，支持审批、拒绝和执行流程。
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.snapshot_service = SnapshotService(db)

    async def _get_pyramid_service(self):
        from app.services.pyramid_service import PyramidService
        return PyramidService(self.db)

    async def execute(self, suggestion_id: str, db: AsyncSession) -> dict[str, Any]:
        """
        执行一条 AI 建议

        步骤：
        1. 查询建议记录
        2. 检查状态（必须是 approved）
        3. 根据 action_type 路由到对应执行器
        4. 更新建议状态为 executed
        5. 返回执行结果
        """
        logger.info(f"开始执行 AI 建议: {suggestion_id}")

        suggestion = await self._get_suggestion(suggestion_id)
        if not suggestion:
            return self._error_result(f"建议不存在: {suggestion_id}", "ERR_SUGGESTION_NOT_FOUND")

        if suggestion.status != "approved":
            logger.error(f"建议状态不是 approved，当前状态: {suggestion.status}")
            return self._error_result(
                f"建议状态不正确，当前状态: {suggestion.status}，需要先审批",
                "ERR_SUGGESTION_NOT_APPROVED"
            )

        try:
            pyramid_id = await self._get_pyramid_id_for_suggestion(suggestion)
            if pyramid_id:
                await self.snapshot_service.create_snapshot(
                    pyramid_id,
                    reason=f"执行建议前备份: {suggestion_id}"
                )

            action_map = {
                "create_node": self._execute_create_node,
                "delete_node": self._execute_delete_node,
                "update_node": self._execute_update_node,
                "split_node": self._execute_split_node,
                "merge_node": self._execute_merge_node,
                "move_node": self._execute_move_node,
                "link_content": self._execute_link_content,
                "update_strategy": self._execute_update_strategy,
                "archive_content": self._execute_archive_content,
                "add_source": self._execute_add_source,
            }

            executor = action_map.get(suggestion.action_type)
            if not executor:
                logger.warning(f"未知的操作类型: {suggestion.action_type}")
                return self._error_result(
                    f"未知的操作类型: {suggestion.action_type}",
                    "ERR_UNKNOWN_ACTION_TYPE"
                )

            result = await executor(suggestion)

            old_status = suggestion.status
            suggestion.status = "executed"
            await self.db.commit()

            logger.info(f"建议 {suggestion_id} 执行成功")

            await self._notify_status_change(suggestion, old_status, "executed")

            return self._success_result(result, f"建议执行成功: {suggestion.action_type}")

        except Exception as e:
            logger.error(f"执行建议 {suggestion_id} 失败: {e}", exc_info=True)
            await self.db.rollback()
            return self._error_result(f"执行失败: {str(e)}", "ERR_EXECUTION_FAILED")

    async def approve(self, suggestion_id: str, db: AsyncSession) -> dict[str, Any]:
        """审批建议"""
        logger.info(f"审批建议: {suggestion_id}")

        suggestion = await self._get_suggestion(suggestion_id)
        if not suggestion:
            return self._error_result(f"建议不存在: {suggestion_id}", "ERR_SUGGESTION_NOT_FOUND")

        if suggestion.status != "pending":
            logger.error(f"建议状态不是 pending，当前状态: {suggestion.status}")
            return self._error_result(
                f"建议状态不正确，当前状态: {suggestion.status}",
                "ERR_SUGGESTION_NOT_PENDING"
            )

        old_status = suggestion.status
        suggestion.status = "approved"
        await self.db.commit()

        logger.info(f"建议 {suggestion_id} 已审批通过")

        await self._notify_status_change(suggestion, old_status, "approved")

        return self._success_result(
            {"suggestion_id": str(suggestion.id), "status": "approved"},
            "建议审批通过"
        )

    async def reject(
        self,
        suggestion_id: str,
        db: AsyncSession,
        reason: Optional[str] = None
    ) -> dict[str, Any]:
        """拒绝建议"""
        logger.info(f"拒绝建议: {suggestion_id}, 原因: {reason}")

        suggestion = await self._get_suggestion(suggestion_id)
        if not suggestion:
            return self._error_result(f"建议不存在: {suggestion_id}", "ERR_SUGGESTION_NOT_FOUND")

        if suggestion.status not in ("pending", "approved"):
            logger.error(f"建议状态不允许拒绝，当前状态: {suggestion.status}")
            return self._error_result(
                f"建议状态不允许拒绝，当前状态: {suggestion.status}",
                "ERR_SUGGESTION_CANNOT_REJECT"
            )

        old_status = suggestion.status
        suggestion.status = "rejected"
        if reason:
            existing_reason = suggestion.reason or ""
            suggestion.reason = f"{existing_reason}\n[拒绝原因: {reason}]".strip()

        await self.db.commit()

        logger.info(f"建议 {suggestion_id} 已拒绝")

        await self._notify_status_change(suggestion, old_status, "rejected")

        return self._success_result(
            {"suggestion_id": str(suggestion.id), "status": "rejected"},
            "建议已拒绝"
        )

    async def _execute_create_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行创建节点操作"""
        params = suggestion.params
        # 使用 suggestion.pyramid_id 而不是 params["pyramid_id"]
        pyramid_id = suggestion.pyramid_id
        
        schema = PyramidNodeCreate(
            name=params.get("name", "新节点"),
            description=params.get("description"),
            parent_id=uuid.UUID(params["parent_id"]) if params.get("parent_id") else None,
            level=0, # Will be calculated by service
            sort_order=0 # Default
        )
        
        service = await self._get_pyramid_service()
        new_node = await service.add_node(pyramid_id, schema)

        logger.info(f"创建节点 '{new_node.name}' 成功，层级: {new_node.level}")

        return {
            "action": "create_node",
            "node_id": str(new_node.id),
            "name": new_node.name,
            "level": new_node.level,
        }

    async def _execute_delete_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行删除节点操作"""
        params = suggestion.params
        node_id = uuid.UUID(params["node_id"])
        
        service = await self._get_pyramid_service()
        node = await service.delete_node(node_id)

        logger.info(f"软删除节点 '{node.name}'")

        return {
            "action": "delete_node",
            "node_id": str(node_id),
            "name": node.name,
        }

    async def _execute_update_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行更新节点操作"""
        params = suggestion.params
        node_id = uuid.UUID(params["node_id"])
        
        # Only include fields that are present in params to avoid overwriting with None
        update_data = {}
        if "name" in params:
            update_data["name"] = params["name"]
        if "description" in params:
            update_data["description"] = params["description"]
            
        schema = PyramidNodeUpdate(**update_data)
        
        service = await self._get_pyramid_service()
        node = await service.update_node(node_id, schema)

        logger.info(f"更新节点 '{node.name}'")

        return {
            "action": "update_node",
            "node_id": str(node_id),
            "new_name": node.name,
            "new_description": node.description,
        }

    async def _execute_split_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行拆分节点操作"""
        params = suggestion.params
        node_id = uuid.UUID(params["node_id"])
        
        suggested_children = params.get("suggested_children", [])
        children_schemas = []
        created_names = []
        
        for child in suggested_children:
            if isinstance(child, str):
                children_schemas.append(PyramidNodeCreate(name=child))
                created_names.append(child)
            elif isinstance(child, dict):
                children_schemas.append(PyramidNodeCreate(
                    name=child.get("name"),
                    description=child.get("description")
                ))
                created_names.append(child.get("name"))
        
        schema = NodeSplitRequest(children=children_schemas)
        
        service = await self._get_pyramid_service()
        created_nodes = await service.split_node(node_id, schema)

        logger.info(f"拆分节点 '{node_id}' 为 {len(created_nodes)} 个子节点")

        return {
            "action": "split_node",
            "node_id": str(node_id),
            "created_children": created_names,
        }

    async def _execute_merge_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行合并节点操作"""
        params = suggestion.params
        
        if "source_node_ids" not in params:
            raise ValueError("合并操作缺少 source_node_ids 参数")
            
        source_node_ids = [uuid.UUID(id) for id in params["source_node_ids"]]
        target_node_name = params.get("target_node_name", "合并节点")
        target_node_desc = params.get("target_node_description")
        # 使用 suggestion.pyramid_id 而不是 params["pyramid_id"]
        pyramid_id = suggestion.pyramid_id
        
        schema = NodeMergeRequest(
            source_node_ids=source_node_ids,
            new_node_name=target_node_name,
            new_node_description=target_node_desc
        )
        
        service = await self._get_pyramid_service()
        new_node = await service.merge_nodes(pyramid_id, schema)

        logger.info(f"合并 {len(source_node_ids)} 个节点到 '{new_node.name}'")

        return {
            "action": "merge_node",
            "merged_node_id": str(new_node.id),
            "source_node_ids": [str(id) for id in source_node_ids],
        }

    async def _execute_move_node(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行移动节点操作"""
        params = suggestion.params
        node_id = uuid.UUID(params["node_id"])
        target_parent_id = uuid.UUID(params["target_parent_id"]) if params.get("target_parent_id") else None
        
        service = await self._get_pyramid_service()
        node = await service.move_node(node_id, new_parent_id=target_parent_id)
        
        logger.info(f"移动节点 '{node.name}' -> parent: {target_parent_id}")
        
        return {
            "action": "move_node",
            "node_id": str(node.id),
            "new_parent_id": str(target_parent_id),
        }

    async def _execute_link_content(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行关联内容操作"""
        params = suggestion.params
        node_id = uuid.UUID(params["node_id"])
        content_ids = params.get("content_ids", [])

        if not content_ids:
            raise ValueError("缺少 content_ids 参数")

        node = await self._get_node(node_id)
        if not node:
            raise ValueError(f"节点不存在: {node_id}")

        linked_count = 0
        for content_id_str in content_ids:
            content_id = uuid.UUID(content_id_str)

            existing = await self._get_content_relation(node_id, content_id)
            if existing:
                continue

            relation = ContentNodeRelation(
                node_id=node_id,
                content_id=content_id,
                confidence=suggestion.confidence or 1.0,
                source="ai_auto",
                is_manual=False,
            )
            self.db.add(relation)
            linked_count += 1

        logger.info(f"关联 {linked_count} 条内容到节点 '{node.name}'")

        return {
            "action": "link_content",
            "node_id": str(node_id),
            "node_name": node.name,
            "linked_count": linked_count,
        }

    async def _execute_update_strategy(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行更新策略操作（信息源）"""
        params = suggestion.params
        source_id = params.get("source_id")

        if not source_id:
            raise ValueError("缺少 source_id 参数")

        source = await self._get_source(uuid.UUID(source_id))
        if not source:
            raise ValueError(f"信息源不存在: {source_id}")

        changes = {}

        if "new_interval" in params:
            old_interval = source.check_interval
            source.check_interval = int(params["new_interval"])
            changes["check_interval"] = {
                "old": old_interval,
                "new": source.check_interval,
            }

        if "new_timeout" in params and hasattr(source, "timeout"):
            old_timeout = getattr(source, "timeout", None)
            source.timeout = int(params["new_timeout"])
            changes["timeout"] = {
                "old": old_timeout,
                "new": source.timeout,
            }

        logger.info(f"更新信息源 '{source.name}' 策略: {changes}")

        return {
            "action": "update_strategy",
            "source_id": str(source.id),
            "source_name": source.name,
            "changes": changes,
        }

    async def _execute_archive_content(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行归档内容操作"""
        params = suggestion.params
        content_ids = params.get("content_ids", [])

        if not content_ids:
            raise ValueError("缺少 content_ids 参数")

        archived_count = 0
        for content_id_str in content_ids:
            content_id = uuid.UUID(content_id_str)
            content = await self._get_content(content_id)
            if content:
                content.lifecycle_status = "ARCHIVED"
                archived_count += 1

        logger.info(f"归档 {archived_count} 条内容")

        return {
            "action": "archive_content",
            "archived_count": archived_count,
        }

    async def _execute_add_source(
        self,
        suggestion: AISuggestion
    ) -> dict[str, Any]:
        """执行添加信息源操作"""
        params = suggestion.params
        name = params.get("name")
        if not name:
             name = f"新信息源 - {datetime.now().strftime('%Y%m%d%H%M')}"
        
        description = params.get("description", "")
        config = {"description": description} if description else {}
        source_type = params.get("type", "web")
        url = params.get("url", "http://pending-configuration")
        
        new_source = InformationSource(
            name=name,
            type=source_type,
            url=url,
            config=config,
            status="pending", # 待配置
        )
        self.db.add(new_source)
        await self.db.flush()
        
        # 关联节点
        node_id = None
        if suggestion.target_type == "pyramid_node" and suggestion.target_id:
            node_id = suggestion.target_id
        elif params.get("node_id"):
             try:
                 node_id = uuid.UUID(params["node_id"])
             except ValueError:
                 pass
                 
        if node_id:
            relation = SourceNodeRelation(
                source_id=new_source.id,
                node_id=node_id,
                weight=1.0
            )
            self.db.add(relation)
        
        logger.info(f"创建信息源 '{name}' 成功")
        
        return {
            "action": "add_source",
            "source_id": str(new_source.id),
            "name": name,
            "status": "pending"
        }

    async def _check_relation_exists(
        self,
        content_id: uuid.UUID,
        node_id: uuid.UUID
    ) -> bool:
        """检查内容关联是否存在"""
        relation = await self._get_content_relation(node_id, content_id)
        return relation is not None

    async def _get_suggestion(self, suggestion_id: str) -> Optional[AISuggestion]:
        """获取建议记录"""
        try:
            sid = uuid.UUID(suggestion_id)
        except ValueError:
            return None

        stmt = select(AISuggestion).where(AISuggestion.id == sid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_node(self, node_id: uuid.UUID) -> Optional[PyramidNode]:
        """获取节点"""
        stmt = select(PyramidNode).where(
            PyramidNode.id == node_id,
            PyramidNode.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_node_children(self, node_id: uuid.UUID) -> list[PyramidNode]:
        """获取节点的子节点"""
        stmt = select(PyramidNode).where(
            PyramidNode.parent_id == node_id,
            PyramidNode.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_content_relations(
        self,
        node_id: uuid.UUID
    ) -> list[ContentNodeRelation]:
        """获取节点的内容关联"""
        stmt = select(ContentNodeRelation).where(
            ContentNodeRelation.node_id == node_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_content_relation(
        self,
        node_id: uuid.UUID,
        content_id: uuid.UUID
    ) -> Optional[ContentNodeRelation]:
        """获取特定的内容关联"""
        stmt = select(ContentNodeRelation).where(
            ContentNodeRelation.node_id == node_id,
            ContentNodeRelation.content_id == content_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_source(self, source_id: uuid.UUID) -> Optional[InformationSource]:
        """获取信息源"""
        stmt = select(InformationSource).where(
            InformationSource.id == source_id,
            InformationSource.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_content(self, content_id: uuid.UUID) -> Optional[ContentItem]:
        """获取内容"""
        stmt = select(ContentItem).where(
            ContentItem.id == content_id,
            ContentItem.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_pyramid_id_for_suggestion(
        self,
        suggestion: AISuggestion
    ) -> Optional[uuid.UUID]:
        """获取建议关联的金字塔 ID"""
        if suggestion.pyramid_id:
            return suggestion.pyramid_id

        if suggestion.target_type == "pyramid_node" and suggestion.target_id:
            node = await self._get_node(suggestion.target_id)
            if node:
                return node.pyramid_id

        if "pyramid_id" in suggestion.params:
            return uuid.UUID(suggestion.params["pyramid_id"])

        if "node_id" in suggestion.params:
            node = await self._get_node(uuid.UUID(suggestion.params["node_id"]))
            if node:
                return node.pyramid_id

        return None

    async def _notify_status_change(
        self,
        suggestion: AISuggestion,
        old_status: str,
        new_status: str
    ) -> None:
        """通知建议状态变更"""
        try:
            from app.services.notification_service import notification_service
            await notification_service.notify_suggestion_status_change(
                suggestion, old_status, new_status
            )
        except Exception as e:
            logger.warning(f"发送建议状态变更通知失败: {e}")

    def _success_result(self, data: Any, message: str) -> dict[str, Any]:
        """构建成功结果"""
        return {
            "success": True,
            "data": data,
            "message": message,
        }

    def _error_result(self, message: str, code: str) -> dict[str, Any]:
        """构建错误结果"""
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        }


suggestion_executor = SuggestionExecutor
