# backend/app/data/seed_content_2026.py

SEEDED_PYRAMIDS = [
    {
        "name": "2026 LLM 模型格局 (Model Landscape 2026)",
        "description": "2026年大语言模型与算力格局",
        "children": [
            {
                "name": "推理与思考 (System 2 Reasoning)",
                "description": "具备慢思考和多步推理能力的模型",
                "children": [
                    {"name": "OpenAI o3 / o3-mini (Chain of Thought)", "description": "OpenAI 第三代推理模型，强化思维链能力"},
                    {"name": "DeepSeek R1 (Reinforcement Learning)", "description": "通过强化学习实现自我进化的推理模型"},
                    {"name": "Google Gemini 2.0 Flash Thinking", "description": "Google 的快速思考模型，兼顾速度与推理"}
                ]
            },
            {
                "name": "前沿通用模型 (Frontier General)",
                "description": "当前最强的通用大语言模型",
                "children": [
                    {"name": "GPT-5 (Orion)", "description": "OpenAI 下一代旗舰模型，原生多模态能力"},
                    {"name": "Claude 3.7 Sonnet / 4.5 Opus", "description": "Anthropic 的最强模型，擅长长文本和代码"},
                    {"name": "Gemini 3 Pro", "description": "Google 的多模态旗舰，超长上下文窗口"}
                ]
            },
            {
                "name": "开源与蒸馏 (Open & Distilled)",
                "description": "最强开源权重模型",
                "children": [
                    {"name": "Llama 4 (405B MoE)", "description": "Meta 的开源旗舰，MoE 架构"},
                    {"name": "DeepSeek-V3 / R1-Distill", "description": "DeepSeek 的开源模型，性价比极高"},
                    {"name": "Mistral Large 3", "description": "欧洲最强开源模型"}
                ]
            },
            {
                "name": "测试时算力 (Test-Time Compute)",
                "description": "推理阶段的算力分配策略",
                "children": [
                    {"name": "动态算力分配 (Dynamic Compute)", "description": "根据问题难度动态分配推理算力"},
                    {"name": "最佳指引 (Best-of-N Sampling)", "description": "生成多个结果并选择最佳答案"}
                ]
            }
        ]
    },
    {
        "name": "智能体认知架构 (Agent Cognitive Architectures)",
        "description": "智能体的核心组件与设计模式",
        "children": [
            {
                "name": "核心组件 (Core Components)",
                "description": "智能体的解剖学结构",
                "children": [
                    {
                        "name": "Skills & Tools (能力层)",
                        "description": "智能体的执行能力",
                        "children": [
                            {"name": "Function Calling", "description": "确定性的工具调用机制"},
                            {"name": "MCP Servers", "description": "模块化能力协议 (Filesystem, Git, API)"},
                            {"name": "Sandboxing", "description": "安全执行环境 (E2B, Docker)"}
                        ]
                    },
                    {
                        "name": "Rules & Alignment (规范层)",
                        "description": "智能体的行为规范",
                        "children": [
                            {"name": "System Prompts", "description": "角色设定与元指令 (Meta-Prompting)"},
                            {"name": "Constitutional AI", "description": "基于规则的自我修正 (RLAIF)"},
                            {"name": "Context Steering", "description": "动态规则注入 (.cursorrules, .trae/rules)"}
                        ]
                    }
                ]
            },
            {
                "name": "编排模式 (Orchestration Patterns)",
                "description": "智能体的协作与流程控制",
                "children": [
                    {"name": "ReAct & Plan-and-Solve", "description": "基础推理与规划循环"},
                    {"name": "Swarm Intelligence", "description": "多智能体群体协作 (OpenAI Swarm)"},
                    {"name": "Hierarchical Agents", "description": "经理-执行者架构 (Supervisor-Worker)"},
                    {"name": "Flow Engineering", "description": "确定性图编排 (LangGraph, LlamaIndex Workflows)"}
                ]
            },
            {
                "name": "记忆系统 (Memory Systems)",
                "description": "智能体的存储与检索",
                "children": [
                    {"name": "Episodic Memory", "description": "情景记忆 (Zep, Mem0)"},
                    {"name": "Semantic Memory", "description": "语义知识库 (RAG, Vector DB)"},
                    {"name": "Procedural Memory", "description": "技能与工具库 (Learned Skills)"}
                ]
            },
            {
                "name": "交互协议 (Protocols)",
                "description": "智能体的通信标准",
                "children": [
                    {"name": "MCP (Model Context Protocol)", "description": "标准化上下文交换"},
                    {"name": "A2A (Agent-to-Agent)", "description": "智能体间通信标准"}
                ]
            }
        ]
    },
    {
        "name": "软件 3.0 与编程范式 (Software 3.0 & Paradigms)",
        "description": "AI 时代的开发模式变革",
        "children": [
            {
                "name": "开发范式 (Dev Paradigms)",
                "description": "新的编程思维方式",
                "children": [
                    {"name": "Vibe Coding", "description": "Just Vibes, No Diffs (Karpathy Style) - For Prototypes"},
                    {"name": "Spec Coding", "description": "Spec-First, AI-Implemented (TDD) - For Engineering"},
                    {"name": "Prompt-Driven Dev", "description": "自然语言即代码"}
                ]
            },
            {
                "name": "自主工程师 (Digital Workers)",
                "description": "全自动化的开发智能体",
                "children": [
                    {"name": "OpenClaw", "description": "本地优先的自主智能体 (Local-First)"},
                    {"name": "Devin / OpenHands", "description": "全栈自主开发"},
                    {"name": "OpenAI Operator", "description": "浏览器操作与任务执行"}
                ]
            },
            {
                "name": "IDE 进化 (IDE Evolution)",
                "description": "下一代开发环境",
                "children": [
                    {"name": "Cursor (Composer)", "description": "上下文感知的代码生成"},
                    {"name": "Trae / Roo Code", "description": "下一代 AI 原生编辑器"}
                ]
            }
        ]
    },
    {
        "name": "本地 AI 与基础设施 (Local AI & Infra)",
        "description": "本地优先的 AI 运行环境",
        "children": [
            {
                "name": "推理引擎 (Inference Engines)",
                "description": "本地模型运行框架",
                "children": [
                    {"name": "Ollama", "description": "跨平台本地运行"},
                    {"name": "vLLM / SGLang", "description": "高吞吐推理服务"},
                    {"name": "MLX", "description": "Apple Silicon 原生加速"},
                    {"name": "Llama.cpp", "description": "边缘设备通用推理"}
                ]
            },
            {
                "name": "端侧硬件 (Edge Hardware)",
                "description": "支持 AI 的硬件设备",
                "children": [
                    {"name": "AI PC / NPU", "description": "Intel Core Ultra, AMD Ryzen AI"},
                    {"name": "Apple Silicon", "description": "M4/M5 Chips"},
                    {"name": "Mobile AI", "description": "Snapdragon 8 Elite"}
                ]
            },
            {
                "name": "隐私与安全 (Privacy & Security)",
                "description": "本地数据保护",
                "children": [
                    {"name": "Local RAG", "description": "本地知识库 (PrivateGPT)"},
                    {"name": "Plaud / Rewind", "description": "个人数据黑匣子"}
                ]
            }
        ]
    }
]
