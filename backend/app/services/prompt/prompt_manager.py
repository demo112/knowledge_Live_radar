"""
⚠️ 已废弃 - DEPRECATED

此模块已废弃，请使用新架构 `app.core.ai.prompt_loader`。

废弃时间: 2026-02-18
替代方案:
- from app.core.ai.prompt_loader import prompt_loader

迁移指南:
- PromptManager.get_prompt_for_scene() → prompt_loader.render_prompt()
- PromptManager.sync_template() → 直接使用 prompt_loader（新架构使用文件系统而非数据库）

此文件将在未来版本中移除。
"""

import warnings

warnings.warn(
    "app.services.prompt.prompt_manager 已废弃，请使用 app.core.ai.prompt_loader",
    DeprecationWarning,
    stacklevel=2
)

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.prompt_template import PromptTemplate
from app.models.prompt_version import PromptVersion
from app.models.ab_test import ABTest

logger = logging.getLogger(__name__)

class PromptManager:
    async def list_templates(self) -> List[PromptTemplate]:
        async with AsyncSessionLocal() as session:
            stmt = select(PromptTemplate)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        async with AsyncSessionLocal() as session:
            return await session.get(PromptTemplate, template_id)

    async def create_version(self, template_id: str, content: str, variables: List[str], created_by: str) -> PromptVersion:
        async with AsyncSessionLocal() as session:
            stmt = select(PromptVersion.version).where(PromptVersion.template_id == template_id).order_by(desc(PromptVersion.version)).limit(1)
            last_version = await session.scalar(stmt) or 0
            
            new_version = PromptVersion(
                template_id=template_id,
                version=last_version + 1,
                content=content,
                variables=variables,
                created_by=created_by
            )
            session.add(new_version)
            await session.commit()
            await session.refresh(new_version)
            return new_version

    async def set_active_version(self, template_id: str, version_id: str) -> None:
        async with AsyncSessionLocal() as session:
            template = await session.get(PromptTemplate, template_id)
            if template:
                template.current_version_id = version_id
                await session.commit()

    async def test_prompt(self, version_id: str, test_input: Dict[str, Any]) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            version = await session.get(PromptVersion, version_id)
            if not version:
                raise ValueError("Version not found")
            
            try:
                formatted_prompt = version.content.format(**test_input)
            except KeyError as e:
                raise ValueError(f"Missing variable: {e}")
                
            start_time = datetime.now()
            try:
                from app.services.ai_service import ai_service
                response = await ai_service.chat_completion([{"role": "user", "content": formatted_prompt}])
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                return {
                    "output": response,
                    "latency_ms": latency,
                    "success": True
                }
            except Exception as e:
                latency = (datetime.now() - start_time).total_seconds() * 1000
                return {
                    "error": str(e),
                    "latency_ms": latency,
                    "success": False
                }

    async def get_prompt_for_scene(self, scene: str, variables: Dict[str, Any]) -> str:
        async with AsyncSessionLocal() as session:
            stmt = select(PromptTemplate).where(PromptTemplate.scene == scene)
            template = await session.scalar(stmt)
            if not template or not template.current_version_id:
                logger.warning(f"No active template for scene {scene}")
                return ""
            
            current_version = await session.get(PromptVersion, template.current_version_id)
            if not current_version:
                 return ""
            
            try:
                return current_version.content.format(**variables)
            except KeyError as e:
                logger.error(f"Missing variable for scene {scene}: {e}")
                return current_version.content

    async def sync_template(self, scene: str, name: str, description: str, content: str, variables: List[str]) -> PromptTemplate:
        async with AsyncSessionLocal() as session:
            stmt = select(PromptTemplate).where(PromptTemplate.scene == scene)
            template = await session.scalar(stmt)
            
            if not template:
                template = PromptTemplate(scene=scene, name=name, description=description)
                session.add(template)
                await session.commit()
                await session.refresh(template)
                logger.info(f"Created new prompt template: {scene}")
            else:
                if template.name != name or template.description != description:
                    template.name = name
                    template.description = description
                    session.add(template)
                    await session.commit()
            
            need_new_version = True
            if template.current_version_id:
                current_version = await session.get(PromptVersion, template.current_version_id)
                if current_version and current_version.content == content and sorted(current_version.variables or []) == sorted(variables):
                    need_new_version = False
            
            if need_new_version:
                stmt = select(PromptVersion.version).where(PromptVersion.template_id == template.id).order_by(desc(PromptVersion.version)).limit(1)
                last_version = await session.scalar(stmt) or 0
                
                new_version = PromptVersion(
                    template_id=template.id,
                    version=last_version + 1,
                    content=content,
                    variables=variables,
                    created_by="system_init"
                )
                session.add(new_version)
                await session.commit()
                await session.refresh(new_version)
                
                template.current_version_id = new_version.id
                session.add(template)
                await session.commit()
                logger.info(f"Updated prompt template version: {scene} -> v{new_version.version}")
            
            return template
            
            version = await session.get(PromptVersion, template.current_version_id)
            if version:
                return version.content.format(**variables)
            return ""

prompt_manager = PromptManager()
