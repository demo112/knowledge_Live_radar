# AI Monitor Dashboard Spec

## Why
目前系统中的 AI 服务调用分散在各个模块（抓取、校验、进化、搜索等），缺乏一个统一的视图来监控 AI 的运行状态。
开发者无法直观地看到 Token 消耗、响应时间、错误率等关键指标，也无法方便地调整 AI 参数（如模型、温度）或在紧急情况下停止服务。
为了提高系统的可观测性和可控性，需要一个统一的 AI 行为监控控制界面。

## What Changes

### Backend
- **新增数据模型**: `AIMetric` 用于记录每次 AI 调用的详细指标（时间、模型、耗时、Token、状态等）。
- **修改 AI Client**: 在 `AIClient` 中增加埋点，自动记录每次调用的指标到数据库。
- **新增服务**: `AIMonitorService` 用于聚合查询指标数据和管理 AI 配置。
- **新增 API**: `/api/v1/ai-monitor` 路由，提供统计数据、日志查询和配置管理接口。

### Frontend
- **新增页面**: `/ai-monitor` (AI 监控台)。
- **新增组件**:
    - **指标卡片**: 展示总调用次数、Token 消耗、平均耗时、错误率。
    - **趋势图表**: 展示调用量和 Token 消耗的时间趋势。
    - **调用日志表**: 展示最近的 AI 调用记录，支持筛选和查看详情。
    - **控制面板**: 允许修改 AI 模型、温度、超时时间等配置，提供“紧急停止”开关。

## Impact
- **Affected Specs**: `ai-service-reliability` (AI 服务可靠性)
- **Affected Code**:
    - `backend/app/core/ai/client.py`: 注入监控逻辑。
    - `backend/app/models/`: 新增 `ai_metric.py`。
    - `backend/app/routers/`: 新增 `ai_monitor.py`。
    - `frontend/src/app/(dashboard)/`: 新增 `ai-monitor/` 页面。

## ADDED Requirements

### Requirement: AI Metrics Collection
系统必须记录每次 AI 调用的以下信息：
- 调用时间 (Timestamp)
- 调用模块/上下文 (Context)
- 使用的模型 (Model)
- 提供商 (Provider: Cloud/Local)
- 耗时 (Latency)
- Token 消耗 (Prompt/Completion/Total)
- 调用状态 (Success/Error)
- 错误信息 (Error Message, if any)

### Requirement: AI Monitor Dashboard
前端界面必须提供以下功能：
- **实时概览**: 展示今日/本周的核心指标（调用量、Token、错误率）。
- **可视化图表**: 以图表形式展示 AI 调用的趋势。
- **日志审计**: 可以查看详细的调用日志，帮助排查问题。
- **配置管理**: 可以实时调整 AI 服务的全局配置（模型、温度等）。
- **紧急控制**: 提供一键停止 AI 服务的开关。

#### Scenario: View AI Health
- **WHEN** 管理员进入 AI 监控台
- **THEN** 可以立即看到当前的 AI 服务健康状态、Token 消耗情况和最近的报错信息。

#### Scenario: Update AI Configuration
- **WHEN** 管理员在控制面板修改模型为 "deepseek-v3" 并保存
- **THEN** 系统立即应用新配置，后续的 AI 调用将使用新模型。

## MODIFIED Requirements
无（主要为新增功能）
