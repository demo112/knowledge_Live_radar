---
description: Predefined pyramid templates for quick creation
---
{
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