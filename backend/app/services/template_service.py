from typing import List, Dict, Any
from uuid import UUID
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
from app.services.pyramid_service import PyramidService
from fastapi import HTTPException

# Hardcoded templates for now
TEMPLATES = {
    "diwta": {
        "name": "DIWTA Model",
        "description": "Data, Information, Wisdom, Truth, Action",
        "nodes": [
            {"title": "Action", "level": 0, "children": [
                {"title": "Truth", "level": 1, "children": [
                    {"title": "Wisdom", "level": 2, "children": [
                        {"title": "Information", "level": 3, "children": [
                             {"title": "Data", "level": 4, "children": []}
                        ]}
                    ]}
                ]}
            ]}
        ]
    },
    "bloom": {
        "name": "Bloom's Taxonomy",
        "description": "Educational learning objectives",
        "nodes": [
            {"title": "Creating", "level": 0, "children": [
                {"title": "Evaluating", "level": 1, "children": [
                    {"title": "Analyzing", "level": 2, "children": [
                        {"title": "Applying", "level": 3, "children": [
                            {"title": "Understanding", "level": 4, "children": [
                                {"title": "Remembering", "level": 5, "children": []}
                            ]}
                        ]}
                    ]}
                ]}
            ]}
        ]
    }
}

class TemplateService:
    def __init__(self, pyramid_service: PyramidService):
        self.pyramid_service = pyramid_service

    def get_templates(self) -> List[Dict[str, Any]]:
        return [{"id": k, "name": v["name"], "description": v["description"]} for k, v in TEMPLATES.items()]

    async def create_from_template(self, template_id: str, name_override: str = None) -> Any:
        if template_id not in TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")
            
        template = TEMPLATES[template_id]
        name = name_override or template["name"]
        
        # 1. Create Pyramid
        pyramid_schema = PyramidCreate(name=name, description=template["description"])
        pyramid = await self.pyramid_service.create_pyramid(pyramid_schema)
        
        # 2. Create Nodes Recursively
        await self._create_nodes_recursive(pyramid.id, template["nodes"], None)
        
        return pyramid

    async def _create_nodes_recursive(self, pyramid_id: UUID, nodes: List[Dict], parent_id: UUID = None):
        for node_data in nodes:
            schema = PyramidNodeCreate(
                name=node_data["title"],
                description=node_data.get("description", ""),
                parent_id=parent_id
            )
            created_node = await self.pyramid_service.add_node(pyramid_id, schema)
            
            if "children" in node_data and node_data["children"]:
                await self._create_nodes_recursive(pyramid_id, node_data["children"], created_node.id)
