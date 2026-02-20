from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.ai.processors.pyramid import pyramid_processor
from app.core.ai.processors.content import content_processor
from app.core.ai.processors.search import search_processor
from app.core.ai.processors.discovery import discovery_processor
from app.core.ai.processors.enhancement import enhancement_processor
from app.core.ai.processors.suggestion import suggestion_processor
from app.core.ai.processors.cognitive_processor import cognitive_processor
from app.schemas.ai import (
    PyramidSuggestResponse, 
    ContentClassificationResponse, 
    SourceAnalyzeResponse,
    NodePlacementResponse
)


class AIFacade:
    """
    AI 能力统一入口。
    委托给具体的处理器执行。
    """
    
    async def find_best_parent_node(
        self,
        new_node_name: str,
        new_node_description: str,
        source_context: str,
        candidate_nodes: List[Dict[str, Any]]
    ) -> NodePlacementResponse:
        """Find the best parent node for a new node."""
        return await pyramid_processor.find_best_parent_node(
            new_node_name, new_node_description, source_context, candidate_nodes
        )

    async def suggest_pyramid_structure(self, name: str, description: str) -> PyramidSuggestResponse:
        """生成金字塔结构建议。"""
        return await pyramid_processor.generate_structure(name, description)

    async def classify_content(self, title: str, content: str, existing_nodes: List[Dict[str, Any]]) -> ContentClassificationResponse:
        """将内容分类到现有节点。"""
        return await content_processor.classify_content(title, content, existing_nodes)

    async def analyze_source(self, url: str, sample_content: str) -> SourceAnalyzeResponse:
        """分析信息源 URL 和内容。"""
        return await content_processor.analyze_source(url, sample_content)

    async def understand_search_intent(self, query: str) -> Dict[str, Any]:
        """理解搜索意图。"""
        return await search_processor.understand_intent(query)

    async def generate_adaptive_queries(self, pyramid_name: str, pyramid_structure_text: str) -> List[Dict[str, str]]:
        """
        Generate adaptive search queries based on pyramid structure context.
        """
        return await discovery_processor.generate_adaptive_queries(pyramid_name, pyramid_structure_text)


    async def validate_content_soft(self, title: str, content: str) -> Dict[str, Any]:
        """软性校验：使用 AI 评估内容质量。"""
        return await enhancement_processor.validate_content_soft(title, content)

    async def generate_summary(self, title: str, content: str) -> Dict[str, Any]:
        """生成内容摘要。"""
        return await enhancement_processor.generate_summary(title, content)

    async def extract_concepts(self, title: str, content: str) -> List[Dict[str, str]]:
        """从内容中提取概念。"""
        return await enhancement_processor.extract_concepts(title, content)

    async def generate_tags(self, title: str, content: str) -> List[str]:
        """生成内容标签。"""
        return await enhancement_processor.generate_tags(title, content)

    async def check_drift(
        self,
        concept_name: str,
        concept_description: str,
        old_content: str,
        new_content: str,
        old_days: int = 30,
        new_days: int = 7
    ) -> Dict[str, Any]:
        """检测概念漂移。"""
        return await enhancement_processor.check_drift(
            concept_name, concept_description, old_content, new_content, old_days, new_days
        )

    async def check_consistency(
        self,
        new_title: str,
        new_text: str,
        existing_content: str
    ) -> Dict[str, Any]:
        """检查新内容与现有内容的一致性。"""
        return await enhancement_processor.check_consistency(new_title, new_text, existing_content)

    async def generate_proposal_reason(
        self,
        match_type: str,
        concept_name: str,
        content_title: str,
        node_name: str = "无"
    ) -> str:
        """生成提案理由。"""
        return await enhancement_processor.generate_proposal_reason(match_type, concept_name, content_title, node_name)

    async def analyze_pyramid_health(self, pyramid_id: str, db: AsyncSession = None) -> Dict[str, Any]:
        """分析金字塔健康状态并生成建议。"""
        return await suggestion_processor.analyze_pyramid_health(pyramid_id, db)

    async def analyze_source_health(self, source_id: str, db: AsyncSession = None) -> Dict[str, Any]:
        """分析信息源健康状态并生成建议。"""
        return await suggestion_processor.analyze_source_health(source_id, db)

    async def analyze_content_metabolism(self, content_ids: List[str], db: AsyncSession = None) -> Dict[str, Any]:
        """分析内容代谢状态并生成建议。"""
        return await suggestion_processor.analyze_content_metabolism(content_ids, db)

    async def analyze_concept_drift(self, node_id: str, db: AsyncSession = None) -> Dict[str, Any]:
        """分析概念漂移并生成建议。"""
        return await suggestion_processor.analyze_concept_drift(node_id, db)

    async def generate_cognitive_model(self, name: str, description: str, context: str = "") -> Dict[str, Any]:
        """生成认知模型。"""
        return await cognitive_processor.generate_cognitive_model(name, description, context)

    async def evolve_cognitive_model(self, current_model: Dict[str, Any], new_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """进化认知模型。"""
        return await cognitive_processor.evolve_cognitive_model(current_model, new_content)

    async def generate_suggestions(self, scene: str, context: Dict[str, Any], db: AsyncSession = None) -> List[Dict[str, Any]]:
        """通用建议生成方法。"""
        if scene == "pyramid_health":
            result = await suggestion_processor.analyze_pyramid_health(context.get("pyramid_id"), db)
            return result.get("suggestions", [])
        elif scene == "source_health":
            result = await suggestion_processor.analyze_source_health(context.get("source_id"), db)
            return result.get("suggestions", [])
        elif scene == "content_metabolism":
            result = await suggestion_processor.analyze_content_metabolism(context.get("content_ids", []), db)
            return result.get("suggestions", [])
        elif scene == "concept_drift":
            result = await suggestion_processor.analyze_concept_drift(context.get("node_id"), db)
            return result.get("suggestions", [])
        else:
            return []


ai_facade = AIFacade()
