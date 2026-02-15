from typing import List, Dict, Any, Optional
from app.core.ai.processors.pyramid import pyramid_processor
from app.core.ai.processors.content import content_processor
from app.core.ai.processors.search import search_processor
from app.schemas.ai import (
    PyramidSuggestResponse, 
    ContentClassificationResponse, 
    SourceAnalyzeResponse
)

class AIFacade:
    """
    Unified entry point for AI capabilities.
    Delegates to specific processors.
    """
    
    async def suggest_pyramid_structure(self, name: str, description: str) -> PyramidSuggestResponse:
        """Generate a pyramid structure suggestion."""
        return await pyramid_processor.generate_structure(name, description)

    async def classify_content(self, title: str, content: str, existing_nodes: List[Dict[str, Any]]) -> ContentClassificationResponse:
        """Classify content into existing nodes."""
        return await content_processor.classify_content(title, content, existing_nodes)

    async def analyze_source(self, url: str, sample_content: str) -> SourceAnalyzeResponse:
        """Analyze a source URL and content."""
        return await content_processor.analyze_source(url, sample_content)

    async def understand_search_intent(self, query: str) -> Dict[str, Any]:
        """Understand search intent."""
        return await search_processor.understand_intent(query)

ai_facade = AIFacade()
