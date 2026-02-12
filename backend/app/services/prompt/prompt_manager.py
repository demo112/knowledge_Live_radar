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
from app.services.ai_service import ai_service # Assuming existing AI service

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
            # Get latest version number
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
            
            # Format prompt
            # Assuming simple f-string format or jinja2
            # content: "Hello {name}"
            try:
                formatted_prompt = version.content.format(**test_input)
            except KeyError as e:
                raise ValueError(f"Missing variable: {e}")
                
            # Call AI
            start_time = datetime.now()
            try:
                # Use a generic completion method from ai_service
                # Assuming ai_service.generate_content or similar exists
                # Or direct call if needed.
                # Here assuming simple text generation
                response = await ai_service.generate_text(formatted_prompt) # Hypothetical method
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
                # Fallback or error
                logger.warning(f"No active template for scene {scene}")
                return "" # Or raise
            
            # Check for active A/B test
            # ...
            
            version = await session.get(PromptVersion, template.current_version_id)
            if version:
                return version.content.format(**variables)
            return ""

prompt_manager = PromptManager()
