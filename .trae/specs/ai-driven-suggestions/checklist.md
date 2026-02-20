# Checklist

## Phase 0: 架构统一

- [x] `app/services/ai_service.py` 已标记为废弃
- [x] `app/services/prompt/prompt_manager.py` 已标记为废弃
- [x] 所有引用已更新为使用 `AIFacade`
- [x] `AIFacade` 新增 `analyze_pyramid_health` 方法
- [x] `AIFacade` 新增 `analyze_source_health` 方法
- [x] `AIFacade` 新增 `analyze_content_metabolism` 方法
- [x] `AIFacade` 新增 `analyze_concept_drift` 方法
- [x] `AIFacade` 新增 `generate_suggestions` 通用方法

## Phase 1: 基础设施

- [x] AISuggestion 模型包含 action_type 字段（枚举类型）
- [x] AISuggestion 模型包含 target_type、target_id、target_name 字段
- [x] AISuggestion 模型包含 reason、params 字段
- [x] AISuggestion 模型包含 status、pyramid_id、source_id 字段
- [x] AISuggestion 模型包含 expires_at 字段
- [x] Alembic 迁移脚本已生成并执行
- [x] `pyramid_health_analysis.md` Prompt 模板已创建
- [x] `source_health_analysis.md` Prompt 模板已创建
- [x] `content_metabolism_analysis.md` Prompt 模板已创建
- [x] `concept_drift_analysis.md` Prompt 模板已创建
- [x] SuggestionProcessor 已创建
- [x] SuggestionProcessor 能正确收集金字塔数据
- [x] SuggestionProcessor 能正确收集信息源数据
- [x] SuggestionProcessor 能正确收集内容数据
- [x] SuggestionProcessor 能调用 AI 服务获取建议
- [x] AI 响应能正确解析并存储到数据库

## Phase 2: 建议执行器

- [x] SuggestionExecutor 服务已创建
- [x] execute 方法能根据 action_type 路由到对应执行器
- [x] 执行结果正确记录

## Phase 3: 服务改造

- [x] HealthEvaluator 已移除硬编码建议逻辑
- [x] HealthEvaluator 已集成 AIFacade
- [x] RestructureAdvisor 已移除硬编码阈值判断
- [x] RestructureAdvisor 已集成 AIFacade
- [x] HealthDetector 已移除硬编码问题描述
- [x] HealthDetector 已集成 AIFacade
- [x] MetabolismService 已移除固定清理建议逻辑
- [x] MetabolismService 已集成 AIFacade
- [x] DriftDetector 已移除内联 Prompt
- [x] DriftDetector 已集成 AIFacade
- [x] LifecycleManager 已移除固定失败原因描述
- [x] LifecycleManager 已集成 AIFacade
- [x] ProposalGenerator 已移除固定原因描述
- [x] ProposalGenerator 已集成 AIFacade

## Phase 4: API 层

- [x] POST /api/v1/pyramids/{id}/analyze 接口可用
- [x] POST /api/v1/sources/{id}/analyze 接口可用
- [x] GET /api/v1/suggestions 接口可用
- [x] POST /api/v1/suggestions/{id}/approve 接口可用
- [x] POST /api/v1/suggestions/{id}/execute 接口可用
- [x] POST /api/v1/suggestions/{id}/reject 接口可用

## Phase 5: 前端适配

- [x] HealthDashboard 组件能正确显示 AI 建议
- [x] 建议详情显示目标、原因、参数
- [x] "接受"/"拒绝"按钮功能正常
- [x] "执行"按钮功能正常（审批后）
- [x] 硬编码翻译键已清理

## Phase 6: 测试与验证

- [x] SuggestionProcessor 单元测试通过
- [x] SuggestionExecutor 单元测试通过
- [x] Prompt 模板输出解析测试通过
- [x] 金字塔分析 → 建议生成 → 审批 → 执行 全链路测试通过
- [x] 信息源分析 → 建议生成 → 审批 → 执行 全链路测试通过

## 验收标准

- [x] 所有 AI 调用统一通过 `AIFacade` 进行
- [x] 所有建议由 AI 生成，无硬编码建议
- [x] 建议包含具体操作目标（节点 ID、名称）
- [x] 建议包含可执行参数
- [x] 用户接受建议后，系统可自动执行
- [x] 前端正确显示 AI 生成的建议内容
- [x] 旧 AI 服务已废弃，无残留引用
