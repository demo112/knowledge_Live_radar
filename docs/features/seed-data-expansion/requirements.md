# Requirements: 扩展 AI 领域知识金字塔 (2026 Frontier Edition)

## Overview

基于用户对 "Vibe Coding", "Spec Coding", "OpenClaw" 等前沿概念的关注，我们需要构建一套反映 **2026 年 AI 范式转移** 的知识体系。不再局限于简单的工具列表，而是深入到 **思维范式 (Paradigms)**、**认知架构 (Cognitive Architectures)** 和 **基础设施 (Infrastructure)** 的变革。

## User Stories

### Story 1: 2026 LLM 模型与算力格局

As a 决策者, I want 了解模型能力的边界和算力转移, so that 我能制定正确的技术路线

**Acceptance Criteria:**

- [ ] AC1: 初始化 "2026 模型格局" 金字塔
  - **Given**: 系统初始化
  - **When**: 执行 `seed_data.py`
  - **Then**: 创建 "2026 LLM 模型格局 (Model Landscape 2026)" 金字塔
  - **And**: 包含以下分支：
    - **推理与思考 (System 2 Reasoning)**:
      - OpenAI o3 / o3-mini (Chain of Thought)
      - DeepSeek R1 (Reinforcement Learning)
      - Google Gemini 2.0 Flash Thinking
    - **前沿通用模型 (Frontier General)**:
      - GPT-5 (Orion) - *Multimodal Native*
      - Claude 3.7 Sonnet / 4.5 Opus - *Agentic Leader*
      - Gemini 3 Pro - *Long Context King*
    - **开源与蒸馏 (Open & Distilled)**:
      - Llama 4 (405B MoE)
      - DeepSeek-V3 / R1-Distill
      - Mistral Large 3
    - **测试时算力 (Test-Time Compute)**:
      - 动态算力分配 (Dynamic Compute)
      - 最佳指引 (Best-of-N Sampling)

### Story 2: 智能体认知架构与核心组件 (Agent Anatomy)

As a 架构师, I want 掌握智能体的解剖学结构, so that 我能设计出能力强大且可控的系统

**Acceptance Criteria:**

- [ ] AC1: 初始化 "智能体认知架构" 金字塔
  - **Given**: 系统初始化
  - **When**: 执行 `seed_data.py`
  - **Then**: 创建 "智能体认知架构 (Agent Cognitive Architectures)" 金字塔
  - **And**: 包含以下分支：
    - **核心组件 (Core Components)**:
      - **Skills & Tools (能力层)**: 
        - **Function Calling**: 确定性工具调用
        - **MCP Servers**: 模块化能力协议 (Filesystem, Git, API)
        - **Sandboxing**: 安全执行环境 (E2B, Docker)
      - **Rules & Alignment (规范层)**:
        - **System Prompts**: 角色设定与元指令 (Meta-Prompting)
        - **Constitutional AI**: 基于规则的自我修正 (RLAIF)
        - **Guardrails**: 边界控制 (NeMo Guardrails, Llama Guard)
        - **Context Steering**: 动态规则注入 (.cursorrules, .trae/rules)
    - **编排模式 (Orchestration Patterns)**:
      - **ReAct & Plan-and-Solve**: 基础推理循环
      - **Swarm Intelligence**: 多智能体群体协作 (OpenAI Swarm)
      - **Hierarchical Agents**: 经理-执行者架构 (Supervisor-Worker)
      - **Flow Engineering**: 确定性图编排 (LangGraph, LlamaIndex Workflows)
    - **记忆系统 (Memory Systems)**:
      - **Episodic Memory**: 情景记忆 (Zep, Mem0)
      - **Semantic Memory**: 语义知识库 (RAG, Vector DB)
      - **Procedural Memory**: 技能与工具库 (Learned Skills)
    - **交互协议 (Protocols)**:
      - **MCP (Model Context Protocol)**: 标准化上下文交换
      - **A2A (Agent-to-Agent)**: 智能体间通信标准

### Story 3: 软件 3.0 与新编程范式

As a 开发者, I want 理解人机协作的新模式, so that 我能在 AI 时代保持竞争力

**Acceptance Criteria:**

- [ ] AC1: 初始化 "新编程范式" 金字塔
  - **Given**: 系统初始化
  - **When**: 执行 `seed_data.py`
  - **Then**: 创建 "软件 3.0 与编程范式 (Software 3.0 & Paradigms)" 金字塔
  - **And**: 包含以下分支：
    - **开发范式 (Dev Paradigms)**:
      - **Vibe Coding**: "Just Vibes, No Diffs" (Karpathy Style) - *For Prototypes*
      - **Spec Coding**: "Spec-First, AI-Implemented" (TDD) - *For Engineering*
      - **Prompt-Driven Dev**: 自然语言即代码
    - **自主工程师 (Digital Workers)**:
      - **OpenClaw**: 本地优先的自主智能体 (Local-First)
      - **Devin / OpenHands**: 全栈自主开发
      - **OpenAI Operator**: 浏览器操作与任务执行
    - **IDE 进化 (IDE Evolution)**:
      - **Cursor (Composer)**: 上下文感知的代码生成
      - **Trae / Roo Code**: 下一代 AI 原生编辑器

### Story 4: 本地 AI 与隐私基础设施

As a 极客/企业用户, I want 掌控我的数据和算力, so that 我能安全地运行 AI

**Acceptance Criteria:**

- [ ] AC1: 初始化 "本地 AI 基础设施" 金字塔
  - **Given**: 系统初始化
  - **When**: 执行 `seed_data.py`
  - **Then**: 创建 "本地 AI 与基础设施 (Local AI & Infra)" 金字塔
  - **And**: 包含以下分支：
    - **推理引擎 (Inference Engines)**:
      - **Ollama**: 跨平台本地运行
      - **vLLM / SGLang**: 高吞吐推理服务
      - **MLX**: Apple Silicon 原生加速
      - **Llama.cpp**: 边缘设备通用推理
    - **端侧硬件 (Edge Hardware)**:
      - **AI PC / NPU**: Intel Core Ultra, AMD Ryzen AI
      - **Apple Silicon**: M4/M5 Chips
      - **Mobile AI**: Snapdragon 8 Elite
    - **隐私与安全 (Privacy & Security)**:
      - **Local RAG**: 本地知识库 (PrivateGPT)
      - **Plaud / Rewind**: 个人数据黑匣子

## Constraints

- 确保术语准确性（如 System 2 Reasoning, Test-Time Compute）。
- 强调 "本地优先" (Local-First) 和 "自主性" (Autonomy) 的趋势。

## Metadata

- 规模：中
- 涉及模块：backend (seed_data)
- 涉及端：Backend
- 创建时间：2026-02-20
- 状态：待确认
