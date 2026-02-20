from typing import List, Dict, Any
from uuid import UUID
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
from app.services.pyramid_service import PyramidService
from fastapi import HTTPException
from app.core.ai.prompt_loader import prompt_loader
import json
import logging

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self, pyramid_service: PyramidService):
        self.pyramid_service = pyramid_service

    async def _load_templates(self) -> Dict[str, Any]:
        try:
            content = await prompt_loader.get_prompt("pyramid/templates")
            if not content:
                logger.error("Templates prompt not found or empty")
                return {}
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return {}

    async def get_templates(self) -> List[Dict[str, Any]]:
        templates = await self._load_templates()
        return [{"id": k, "name": v["name"], "description": v["description"]} for k, v in templates.items()]

    async def create_from_template(self, template_id: str, name_override: str = None) -> Any:
        templates = await self._load_templates()
        if template_id not in templates:
            raise HTTPException(status_code=404, detail="未找到模板")
            
        template = templates[template_id]
        return await self.import_template(template, name_override)

    async def import_template(self, template_data: Dict[str, Any], name_override: str = None) -> Any:
        """Import a pyramid structure from a template dictionary"""
        name = name_override or template_data.get("name", "Imported Pyramid")
        description = template_data.get("description", "")
        
        pyramid_schema = PyramidCreate(name=name, description=description)
        pyramid = await self.pyramid_service.create_pyramid(pyramid_schema)
        
        nodes = template_data.get("nodes", [])
        await self._create_nodes_recursive(pyramid.id, nodes, None)
        
        return await self.pyramid_service.get_pyramid_details(pyramid.id)

    async def export_template(self, pyramid_id: UUID) -> Dict[str, Any]:
        """Export a pyramid structure as a template"""
        pyramid = await self.pyramid_service.get_pyramid(pyramid_id)
        if not pyramid:
            raise HTTPException(status_code=404, detail="未找到金字塔")
            
        # Helper to build recursive node structure
        def build_node_tree(nodes, parent_id=None):
            tree = []
            # Filter nodes that belong to this parent
            children = [n for n in nodes if n.parent_id == parent_id]
            # Sort by level or custom order if available (using level for now as proxy for hierarchy)
            # Actually siblings have same level, need sort_order?
            # Assuming sort_order is present on node model
            children.sort(key=lambda x: getattr(x, 'sort_order', 0))
            
            for node in children:
                node_dict = {
                    "title": node.name,
                    "description": node.description or "",
                    "level": node.level,
                    "children": build_node_tree(nodes, node.id)
                }
                tree.append(node_dict)
            return tree

        return {
            "name": pyramid.name,
            "description": pyramid.description,
            "nodes": build_node_tree(pyramid.nodes)
        }

    async def _create_nodes_recursive(self, pyramid_id: UUID, nodes: List[Dict], parent_id: UUID = None):
        for i, node_data in enumerate(nodes):
            schema = PyramidNodeCreate(
                name=node_data["title"],
                description=node_data.get("description", ""),
                parent_id=parent_id,
                # Pass explicit sort_order if we want to preserve order
            )
            created_node = await self.pyramid_service.add_node(pyramid_id, schema)
            
            if "children" in node_data and node_data["children"]:
                await self._create_nodes_recursive(pyramid_id, node_data["children"], created_node.id)
