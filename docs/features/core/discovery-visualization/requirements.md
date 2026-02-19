# Requirements: 发现流程可视化 (Discovery Process Visualization)

## Overview

在信息源界面的"发现"功能中，增加一个可视化的流程展示组件。当用户点击"Discover New Sources"按钮后，系统将启动后端发现任务，并通过 Server-Sent Events (SSE) 实时推送各个阶段的执行状态和详细日志。

**核心目标**：让用户清晰感知系统在"做什么"，特别是那些非 LLM 的后台处理过程（如关键词提取、网络搜索、数据过滤等）。

## User Stories

### Story 1: 全流程实时可视化

As a 用户, I want 在点击发现按钮后，看到一个详细的流程执行视图, So that 我能了解系统是如何一步步找到新信息源的，而不是面对一个未知的加载状态。

**Acceptance Criteria:**

- [ ] AC1: 阶段展示 (Stage Visualization)
  - **Given**: 发现任务启动
  - **When**: 任务进入不同阶段
  - **Then**: 界面高亮显示当前所处阶段：
    1.  **关键词提取 (Keyword Extraction)**: 分析金字塔节点，生成搜索关键词。
    2.  **网络搜索 (Web Search)**: 对每个关键词执行 DuckDuckGo 搜索。
    3.  **结果过滤 (Filtering & Deduplication)**: 检查 URL 是否已存在或重复。
    4.  **提案生成 (Proposal Creation)**: 将有效结果转换为待审批提案。

- [ ] AC2: 细粒度进度反馈 (Granular Progress)
  - **Given**: 任务处于"网络搜索"阶段
  - **When**: 后端正在搜索某个关键词（例如 "Python"）
  - **Then**: 
    - 界面显示当前正在处理的关键词："Searching for 'Python'..."
    - 搜索完成后显示结果数量："Found 5 candidates for 'Python'"

- [ ] AC3: 过滤逻辑展示 (Filtering Logic)
  - **Given**: 任务处于"结果过滤"阶段
  - **When**: 发现重复 URL
  - **Then**: 
    - 界面显示过滤统计："Skipped 2 (Already exists)", "Skipped 1 (Pending approval)"
    - 有效结果显示为："Valid candidate: [Title]"

- [ ] AC4: 实时流式响应 (SSE Implementation)
  - **Given**: 点击发现按钮
  - **When**: 建立连接
  - **Then**: 
    - 前端建立 SSE 连接 (`/api/v1/sources/discover/stream`)
    - 后端通过 SSE 推送事件：`stage_start`, `log`, `progress`, `stage_end`, `finish`
    - 任务完成后自动关闭连接并刷新列表

## Constraints

- **后端架构**: 使用 Python FastAPI 的 `StreamingResponse` 实现 SSE。
- **前端组件**: 使用 React 组件接收 SSE 事件并更新 UI 状态（进度条、日志列表、当前阶段指示器）。
- **非阻塞**: 发现过程应在后台运行，但前台需保持连接以接收实时更新。

## Out of Scope

- 对 LLM 的深度集成（当前发现流程暂不涉及 LLM 生成，仅基于规则和搜索）。
- 复杂的图表可视化（使用简单的进度条和日志列表即可）。

## Metadata

- 规模: 小
- 涉及模块: `source-discovery`, `ui-components`
- 涉及端: Backend, Frontend
- 状态: 规划中 (Draft)
