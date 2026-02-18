from typing import List, Dict, Any
from uuid import UUID
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate
from app.services.pyramid_service import PyramidService
from fastapi import HTTPException

# Enhanced templates based on requirements
TEMPLATES = {
    "ai_dev_tools": {
        "name": "AI 开发工具链",
        "description": "IDE、框架、库、部署工具等",
        "nodes": [
            {"title": "开发框架", "level": 0, "children": [
                {"title": "深度学习框架", "level": 1, "children": [
                    {"title": "PyTorch", "level": 2, "children": []},
                    {"title": "TensorFlow", "level": 2, "children": []},
                    {"title": "JAX", "level": 2, "children": []}
                ]},
                {"title": "应用开发框架", "level": 1, "children": [
                    {"title": "LangChain", "level": 2, "children": []},
                    {"title": "LlamaIndex", "level": 2, "children": []}
                ]}
            ]},
            {"title": "基础设施", "level": 0, "children": [
                {"title": "模型部署", "level": 1, "children": [
                    {"title": "vLLM", "level": 2, "children": []},
                    {"title": "TGI", "level": 2, "children": []},
                    {"title": "TensorRT-LLM", "level": 2, "children": []}
                ]},
                {"title": "向量数据库", "level": 1, "children": [
                    {"title": "Milvus", "level": 2, "children": []},
                    {"title": "Qdrant", "level": 2, "children": []},
                    {"title": "Chroma", "level": 2, "children": []}
                ]}
            ]},
            {"title": "辅助工具", "level": 0, "children": [
                {"title": "评估工具", "level": 1, "children": [
                    {"title": "Ragas", "level": 2, "children": []},
                    {"title": "DeepEval", "level": 2, "children": []}
                ]}
            ]}
        ]
    },
    "agent_ecosystem": {
        "name": "Agent 生态",
        "description": "Agent 框架、工具调用、多 Agent 协作等",
        "nodes": [
            {"title": "Agent 框架", "level": 0, "children": [
                {"title": "单体 Agent", "level": 1, "children": [
                    {"title": "AutoGPT", "level": 2, "children": []},
                    {"title": "BabyAGI", "level": 2, "children": []}
                ]},
                {"title": "多 Agent 协作", "level": 1, "children": [
                    {"title": "AutoGen", "level": 2, "children": []},
                    {"title": "MetaGPT", "level": 2, "children": []},
                    {"title": "CrewAI", "level": 2, "children": []}
                ]}
            ]},
            {"title": "关键能力", "level": 0, "children": [
                {"title": "工具调用", "level": 1, "children": []},
                {"title": "记忆管理", "level": 1, "children": []},
                {"title": "规划能力", "level": 1, "children": []}
            ]}
        ]
    },
    "prompt_engineering": {
        "name": "Prompt 工程",
        "description": "提示词技术、优化方法、评估方法等",
        "nodes": [
            {"title": "基础技术", "level": 0, "children": [
                {"title": "Zero-shot", "level": 1, "children": []},
                {"title": "Few-shot", "level": 1, "children": []},
                {"title": "CoT (思维链)", "level": 1, "children": []}
            ]},
            {"title": "高级策略", "level": 0, "children": [
                {"title": "ToT (思维树)", "level": 1, "children": []},
                {"title": "ReAct", "level": 1, "children": []},
                {"title": "RAG 增强", "level": 1, "children": []}
            ]},
            {"title": "安全与防御", "level": 0, "children": [
                {"title": "提示词注入防御", "level": 1, "children": []},
                {"title": "越狱检测", "level": 1, "children": []}
            ]}
        ]
    },
    "model_capabilities": {
        "name": "模型应用能力",
        "description": "文本生成、代码生成、多模态等",
        "nodes": [
            {"title": "文本处理", "level": 0, "children": [
                {"title": "文本生成", "level": 1, "children": []},
                {"title": "摘要提取", "level": 1, "children": []},
                {"title": "情感分析", "level": 1, "children": []}
            ]},
            {"title": "代码能力", "level": 0, "children": [
                {"title": "代码补全", "level": 1, "children": []},
                {"title": "代码解释", "level": 1, "children": []},
                {"title": "单元测试生成", "level": 1, "children": []}
            ]},
            {"title": "多模态", "level": 0, "children": [
                {"title": "文生图", "level": 1, "children": []},
                {"title": "图生文", "level": 1, "children": []},
                {"title": "视频生成", "level": 1, "children": []}
            ]}
        ]
    },
    "trend_tracking": {
        "name": "热点追踪",
        "description": "新模型发布、重大更新、行业动态等",
        "nodes": [
            {"title": "模型发布", "level": 0, "children": [
                {"title": "闭源模型", "level": 1, "children": [
                    {"title": "GPT 系列", "level": 2, "children": []},
                    {"title": "Claude 系列", "level": 2, "children": []},
                    {"title": "Gemini 系列", "level": 2, "children": []}
                ]},
                {"title": "开源模型", "level": 1, "children": [
                    {"title": "Llama 系列", "level": 2, "children": []},
                    {"title": "Qwen 系列", "level": 2, "children": []},
                    {"title": "Mistral 系列", "level": 2, "children": []}
                ]}
            ]},
            {"title": "行业动态", "level": 0, "children": [
                {"title": "政策法规", "level": 1, "children": []},
                {"title": "企业融资", "level": 1, "children": []},
                {"title": "应用落地", "level": 1, "children": []}
            ]}
        ]
    },
    "diwta": {
        "name": "DIWTA 模型",
        "description": "数据 (Data) - 信息 (Information) - 智慧 (Wisdom) - 真理 (Truth) - 行动 (Action)",
        "nodes": [
            {"title": "行动 (Action)", "level": 0, "children": [
                {"title": "真理 (Truth)", "level": 1, "children": [
                    {"title": "智慧 (Wisdom)", "level": 2, "children": [
                        {"title": "信息 (Information)", "level": 3, "children": [
                             {"title": "数据 (Data)", "level": 4, "children": []}
                        ]}
                    ]}
                ]}
            ]}
        ]
    },
    "bloom": {
        "name": "布鲁姆分类法",
        "description": "教育学习目标分类 (Bloom's Taxonomy)",
        "nodes": [
            {"title": "创造 (Creating)", "level": 0, "children": [
                {"title": "评价 (Evaluating)", "level": 1, "children": [
                    {"title": "分析 (Analyzing)", "level": 2, "children": [
                        {"title": "应用 (Applying)", "level": 3, "children": [
                            {"title": "理解 (Understanding)", "level": 4, "children": [
                                {"title": "记忆 (Remembering)", "level": 5, "children": []}
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
            raise HTTPException(status_code=404, detail="未找到模板")
            
        template = TEMPLATES[template_id]
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
