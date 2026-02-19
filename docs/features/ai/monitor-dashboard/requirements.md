# Requirements: AI 监控仪表盘 (AI Monitor Dashboard)

## Overview

目前系统中的 AI 服务调用分散在各个模块（抓取、校验、进化、搜索等），缺乏一个统一的视图来监控 AI 的运行状态。
开发者无法直观地看到 Token 消耗、响应时间、错误率等关键指标，也无法方便地调整 AI 参数（如模型、温度）或在紧急情况下停止服务。
为了提高系统的可观测性和可控性，需要一个统一的 AI 行为监控控制界面。

## User Stories

### Story 1: AI 指标采集 (Metrics Collection)

As a 系统, I want 自动记录每次 AI 调用的详细指标, So that 我可以后续进行统计分析和审计。

**Acceptance Criteria:**

- [ ] AC1: 记录核心指标
  - **Given**: 系统发起一次 AI 调用（通过 `AIClient`）
  - **When**: 调用完成（成功或失败）
  - **Then**: 
    - 自动创建一条 `AIMetric` 记录
    - 包含字段：`timestamp`, `context` (模块名), `model`, `provider`, `latency_ms`, `tokens_prompt`, `tokens_completion`, `tokens_total`, `status`, `error_message`

- [ ] AC2: 错误捕获
  - **Given**: AI 调用发生异常（如超时、API 错误）
  - **When**: 记录指标
  - **Then**: 
    - `status` 标记为 `ERROR`
    - `error_message` 记录具体的异常堆栈摘要

### Story 2: 监控仪表盘 (Monitor Dashboard)

As a 管理员, I want 一个可视化的仪表盘来查看 AI 运行状态, So that 我能快速了解系统健康度和成本消耗。

**Acceptance Criteria:**

- [ ] AC1: 实时概览
  - **Given**: 进入 `/ai-monitor` 页面
  - **When**: 页面加载
  - **Then**: 
    - 展示“今日调用量”、“今日 Token 消耗”、“平均耗时”、“错误率”四个核心指标卡片
    - 展示“最近 24 小时调用趋势”折线图

- [ ] AC2: 调用日志审计
  - **Given**: 在仪表盘下方
  - **When**: 查看日志列表
  - **Then**: 
    - 按时间倒序展示最近的 AI 调用
    - 支持按“状态”（成功/失败）、“模块”进行筛选
    - 点击某条日志可查看完整的 Prompt 和 Response（如果有权限）

### Story 3: AI 配置管理 (Configuration Management)

As a 管理员, I want 实时调整 AI 参数或紧急停止服务, So that 我可以在不重启服务的情况下应对突发状况。

**Acceptance Criteria:**

- [ ] AC1: 动态配置修改
  - **Given**: 控制面板区域
  - **When**: 修改默认模型为 `gpt-4o` 并保存
  - **Then**: 
    - 系统配置立即更新
    - 后续的 AI 调用（未指定特定模型的）自动使用新模型

- [ ] AC2: 紧急停止开关 (Kill Switch)
  - **Given**: 发现 AI 服务异常消耗大量 Token
  - **When**: 点击“紧急停止”开关
  - **Then**: 
    - 全局 AI 服务状态变为 `STOPPED`
    - 所有新的 AI 调用请求直接返回错误或默认值，不再请求外部 API

## Data Model

### AIMetric
- `id`: UUID
- `timestamp`: DateTime
- `context`: String (e.g., "summary", "evolution")
- `model`: String
- `provider`: String
- `latency_ms`: Float
- `tokens_prompt`: Integer
- `tokens_completion`: Integer
- `tokens_total`: Integer
- `status`: Enum (SUCCESS, ERROR)
- `error_message`: String (Optional)

## Metadata

- 规模: 中
- 涉及模块: `ai-core`, `monitor-service`
- 涉及端: Backend, Frontend
- 创建时间: 2026-02-18
- 状态: 进行中
