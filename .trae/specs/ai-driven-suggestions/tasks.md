# Tasks

## Phase 0: 架构统一（优先）

- [x] Task 0.1: 废弃旧 AI 服务
  - [x] 0.1.1 标记 `app/services/ai_service.py` 为废弃
  - [x] 0.1.2 标记 `app/services/prompt/prompt_manager.py` 为废弃
  - [x] 0.1.3 更新所有引用，改为使用 `AIFacade`

- [x] Task 0.2: 扩展 AIFacade
  - [x] 0.2.1 新增 `analyze_pyramid_health(pyramid_id)` 方法
  - [x] 0.2.2 新增 `analyze_source_health(source_id)` 方法
  - [x] 0.2.3 新增 `analyze_content_metabolism(content_ids)` 方法
  - [x] 0.2.4 新增 `analyze_concept_drift(node_id)` 方法
  - [x] 0.2.5 新增 `generate_suggestions(scene, context)` 通用方法

## Phase 1: 基础设施

- [x] Task 1: 扩展 AISuggestion 数据模型
  - [x] 1.1 添加 `action_type` 字段（枚举类型）
  - [x] 1.2 添加 `target_type`、`target_id`、`target_name` 字段
  - [x] 1.3 添加 `reason`、`params` 字段
  - [x] 1.4 添加 `status`、`pyramid_id`、`source_id` 字段
  - [x] 1.5 添加 `expires_at` 字段
  - [x] 1.6 生成 Alembic 迁移脚本

- [x] Task 2: 创建 Prompt 模板
  - [x] 2.1 创建 `pyramid_health_analysis.md`
  - [x] 2.2 创建 `source_health_analysis.md`
  - [x] 2.3 创建 `content_metabolism_analysis.md`
  - [x] 2.4 创建 `concept_drift_analysis.md`

- [x] Task 3: 创建 SuggestionProcessor
  - [x] 3.1 创建 `app/core/ai/processors/suggestion.py`
  - [x] 3.2 实现 `analyze_pyramid_health` 方法
  - [x] 3.3 实现 `analyze_source_health` 方法
  - [x] 3.4 实现 `analyze_content_metabolism` 方法
  - [x] 3.5 实现 `analyze_concept_drift` 方法
  - [x] 3.6 实现数据收集逻辑（节点树、内容统计等）
  - [x] 3.7 实现 AI 响应解析和存储

## Phase 2: 建议执行器

- [x] Task 4: 实现 SuggestionExecutor
  - [x] 4.1 创建 `app/services/suggestion_executor.py`
  - [x] 4.2 实现 `execute(suggestion_id)` 方法
  - [x] 4.3 根据 `action_type` 路由到对应执行器
  - [x] 4.4 复用现有 `DecisionExecutor` 的执行逻辑
  - [x] 4.5 实现执行结果记录

## Phase 3: 服务改造

- [x] Task 5: 改造 HealthEvaluator
  - [x] 5.1 移除硬编码建议逻辑
  - [x] 5.2 调用 `AIFacade.analyze_pyramid_health`
  - [x] 5.3 更新返回数据结构

- [x] Task 6: 改造 RestructureAdvisor
  - [x] 6.1 移除硬编码阈值判断
  - [x] 6.2 调用 `AIFacade.analyze_pyramid_health`
  - [x] 6.3 保留阈值作为 Prompt 上下文参考

- [x] Task 7: 改造 HealthDetector
  - [x] 7.1 移除硬编码问题描述
  - [x] 7.2 调用 AI 生成具体建议

- [x] Task 8: 改造 MetabolismService
  - [x] 8.1 移除固定清理建议逻辑
  - [x] 8.2 调用 `AIFacade.analyze_content_metabolism`

- [x] Task 9: 改造 DriftDetector
  - [x] 9.1 移除内联 Prompt
  - [x] 9.2 调用 `AIFacade.analyze_concept_drift`

- [x] Task 10: 改造 LifecycleManager
  - [x] 10.1 移除固定失败原因描述
  - [x] 10.2 调用 `AIFacade.analyze_source_health`

- [x] Task 11: 改造 ProposalGenerator
  - [x] 11.1 移除固定原因描述
  - [x] 11.2 使用 AI 生成原因

## Phase 4: API 层

- [x] Task 12: 新增建议相关 API
  - [x] 12.1 `POST /api/v1/pyramids/{id}/analyze` - 触发金字塔分析
  - [x] 12.2 `POST /api/v1/sources/{id}/analyze` - 触发信息源分析
  - [x] 12.3 `GET /api/v1/suggestions` - 获取建议列表
  - [x] 12.4 `POST /api/v1/suggestions/{id}/approve` - 审批建议
  - [x] 12.5 `POST /api/v1/suggestions/{id}/execute` - 执行建议
  - [x] 12.6 `POST /api/v1/suggestions/{id}/reject` - 拒绝建议

## Phase 5: 前端适配

- [x] Task 13: 改造 HealthDashboard 组件
  - [x] 13.1 适配新的建议数据结构
  - [x] 13.2 显示建议详情（目标、原因、参数）
  - [x] 13.3 添加"接受"/"拒绝"按钮
  - [x] 13.4 添加"执行"按钮（审批后）

- [x] Task 14: 清理硬编码翻译键
  - [x] 14.1 删除 `en.json` 中的 `Health.empty_nodes_desc` 等键
  - [x] 14.2 删除 `zh.json` 中对应的键（如存在）

## Phase 6: 测试与验证

- [x] Task 15: 编写单元测试
  - [x] 15.1 `SuggestionProcessor` 测试
  - [x] 15.2 `SuggestionExecutor` 测试
  - [x] 15.3 Prompt 模板输出解析测试

- [x] Task 16: 集成测试
  - [x] 16.1 金字塔分析 → 建议生成 → 审批 → 执行 全链路测试
  - [x] 16.2 信息源分析 → 建议生成 → 审批 → 执行 全链路测试

# Task Dependencies

- Task 0.1, 0.2 无依赖，可立即开始
- Task 1, 2, 3 依赖 Task 0
- Task 4 依赖 Task 1
- Task 5-11 依赖 Task 3
- Task 12 依赖 Task 3, Task 4
- Task 13, 14 依赖 Task 12
- Task 15, 16 依赖 Task 1-14

# Parallelizable Work

- Task 0.1 和 Task 0.2 可并行
- Task 1, 2, 3 可并行
- Task 5-11 可并行（改造不同服务）
- Task 13 和 Task 14 可并行