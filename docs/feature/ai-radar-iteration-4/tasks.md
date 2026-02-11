# 实现计划：迭代 4 - 自我进化

## 概述

本实现计划将迭代 4 的设计分解为可执行的编码任务。任务按照依赖关系排序，确保每个任务都建立在前一个任务的基础上。迭代 4 聚焦于系统的自我进化能力，包括健康检测、重构建议、热点管理、概念漂移、策略自适应、定时任务和配置管理。

## 技术栈

- 后端：Python FastAPI
- 前端：Next.js + Tailwind CSS
- AI 服务：硅基流动 API
- 数据库：PostgreSQL/SQLite
- 定时任务：APScheduler

## 任务列表

- [ ] 1. 数据模型扩展
  - [ ] 1.1 创建热点话题数据模型
    - 创建 `backend/app/models/hotspot.py`
    - 定义 Hotspot 模型，包含 id、topic_name、description、status、mention_count、recent_7d_count、previous_7d_count、growth_rate、display_priority、related_node_ids、related_content_ids、first_seen_at、last_mentioned_at、status_changed_at 等字段
    - 创建 `backend/app/models/hotspot_event.py`
    - 定义 HotspotEvent 模型，包含 id、hotspot_id、event_type、old_status、new_status、trigger_condition、operator 等字段
    - _Requirements: 3.1-3.8_

  - [ ] 1.2 创建概念定义版本数据模型
    - 创建 `backend/app/models/concept_definition.py`
    - 定义 ConceptDefinition 模型，包含 id、term、definition、context_examples、version、drift_detected、drift_evidence、previous_version_id、proposal_id、is_current 等字段
    - _Requirements: 4.5_

  - [ ] 1.3 创建健康报告数据模型
    - 创建 `backend/app/models/health_report.py`
    - 定义 HealthReport 模型，包含 id、report_type、overall_score、pyramid_scores、source_health_score、content_coverage_score、hotspot_distribution、approval_backlog、crawl_stats、issues 等字段
    - _Requirements: 1.1-1.9_

  - [ ] 1.4 创建策略调整记录数据模型
    - 创建 `backend/app/models/strategy_adjustment.py`
    - 定义 StrategyAdjustment 模型，包含 id、source_id、adjustment_type、old_value、new_value、reason、expected_effect、requires_approval、proposal_id、applied_at 等字段
    - _Requirements: 5.6_

  - [ ] 1.5 创建定时任务和执行记录数据模型
    - 创建 `backend/app/models/scheduled_task.py`
    - 定义 ScheduledTask 模型，包含 id、task_name、task_type、cron_expression、is_active、last_run_at、next_run_at、is_running、max_retries、retry_delay_seconds 等字段
    - 创建 `backend/app/models/task_execution.py`
    - 定义 TaskExecution 模型，包含 id、task_id、status、started_at、ended_at、duration_seconds、result、error_message、retry_count 等字段
    - _Requirements: 7.1-7.7_

  - [ ] 1.6 创建配置变更历史数据模型
    - 创建 `backend/app/models/config_history.py`
    - 定义 ConfigHistory 模型，包含 id、config_key、old_value、new_value、changed_by 等字段
    - _Requirements: 8.5_

  - [ ] 1.7 创建数据库迁移脚本
    - 使用 Alembic 创建迁移脚本
    - 执行迁移创建新表
    - _Requirements: 1.1-1.7_

- [ ] 2. 检查点 - 数据模型完成
  - 确保所有测试通过，如有问题请询问用户

- [ ] 3. 系统配置管理服务
  - [ ] 3.1 实现配置管理服务
    - 创建 `backend/app/services/config/configuration_service.py`
    - 实现 ConfigurationService 类，包含 load、get、set、validate、get_all、get_history、reload 方法
    - 实现环境变量加载、配置文件解析、默认值回退
    - 实现配置值验证逻辑（类型检查、范围验证）
    - 实现热更新机制（内存缓存 + 变更回调）
    - _Requirements: 8.1-8.7_

  - [ ]* 3.2 编写配置管理属性测试
    - **Property 20: 配置验证拒绝无效值**
    - **Property 21: 配置变更历史完整性**
    - **Property 22: 配置热更新往返一致性**
    - **Validates: Requirements 8.4, 8.5, 8.6**

- [ ] 4. 定时任务调度服务
  - [ ] 4.1 实现定时任务调度服务
    - 创建 `backend/app/services/scheduler/scheduler_service.py`
    - 创建 `backend/app/services/scheduler/task_registry.py`
    - 实现 SchedulerService 类，包含 register_task、start、stop、trigger_task、pause_task、resume_task 方法
    - 实现任务锁机制（防止并发执行）
    - 实现带重试的任务执行（指数退避）
    - 实现执行历史记录和查询
    - _Requirements: 7.1-7.7_

  - [ ]* 4.2 编写定时任务属性测试
    - **Property 16: 任务执行记录完整性**
    - **Property 17: 任务重试策略正确性**
    - **Property 18: 任务暂停/恢复一致性**
    - **Property 19: 任务并发执行防护**
    - **Validates: Requirements 7.2, 7.3, 7.5, 7.6**

- [ ] 5. 检查点 - 基础设施完成
  - 确保配置管理和定时任务调度正常工作
  - 如有问题请询问用户

- [ ] 6. 系统健康检测服务
  - [ ] 6.1 实现系统健康检测器
    - 创建 `backend/app/services/evolution/health_detector.py`
    - 实现 HealthDetector 类，包含 run_full_detection、evaluate_pyramid_structure、evaluate_source_health、evaluate_hotspot_distribution、evaluate_content_coverage、evaluate_approval_backlog 方法
    - 实现加权平均整体评分计算
    - 实现问题检测和报告生成
    - 实现健康报告持久化
    - _Requirements: 1.1-1.9_

  - [ ]* 6.2 编写健康检测属性测试
    - **Property 1: 健康评分范围不变量**
    - **Property 2: 健康问题触发一致性**
    - **Property 3: 热点分布统计完整性**
    - **Property 4: 审批积压统计正确性**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.9**

- [ ] 7. 金字塔重构建议服务
  - [ ] 7.1 实现金字塔重构建议器
    - 创建 `backend/app/services/evolution/restructure_advisor.py`
    - 实现 RestructureAdvisor 类，包含 analyze_pyramid、detect_content_overload、detect_empty_nodes、detect_deep_hierarchy、detect_too_many_siblings 方法
    - 实现 generate_proposals 方法，为检测到的问题生成 Change_Proposal（复用迭代 3 的 Proposal_Generator）
    - 创建金字塔结构分析 Prompt 模板
    - _Requirements: 2.1-2.7_

  - [ ]* 7.2 编写重构建议属性测试
    - **Property 5: 重构提案触发正确性**
    - **Property 6: 重构提案内容完整性**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6**

- [ ] 8. 热点生命周期管理服务
  - [ ] 8.1 实现热点生命周期管理器
    - 创建 `backend/app/services/evolution/hotspot_manager.py`
    - 实现 HotspotManager 类，包含 update_lifecycle、detect_emerging_topics、evaluate_transitions、apply_transition 方法
    - 实现优先级权重调整逻辑
    - 实现手动状态调整功能
    - 实现生命周期轨迹记录和查询
    - _Requirements: 3.1-3.8_

  - [ ]* 8.2 编写热点生命周期属性测试
    - **Property 7: 热点生命周期状态转换正确性**
    - **Property 8: 热点优先级权重单调性**
    - **Property 9: 热点生命周期轨迹完整性**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

- [ ] 9. 检查点 - 核心进化服务完成
  - 确保健康检测、重构建议、热点管理正常工作
  - 如有问题请询问用户

- [ ] 10. 概念漂移检测服务
  - [ ] 10.1 实现概念漂移检测器
    - 创建 `backend/app/services/evolution/concept_drift_detector.py`
    - 实现 ConceptDriftDetector 类，包含 run_detection、extract_term_context、compare_contexts 方法
    - 实现 generate_drift_proposals 方法，为检测到的漂移生成 Change_Proposal
    - 实现术语定义版本管理（save_definition_version、get_definition_history）
    - 创建概念漂移检测 Prompt 模板
    - _Requirements: 4.1-4.6_

  - [ ]* 10.2 编写概念漂移属性测试
    - **Property 10: 概念漂移检测阈值一致性**
    - **Property 11: 概念漂移提案完整性**
    - **Property 12: 术语定义版本链完整性**
    - **Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.6**

- [ ] 11. 抓取策略自适应服务
  - [ ] 11.1 实现抓取策略优化器
    - 创建 `backend/app/services/evolution/strategy_optimizer.py`
    - 实现 StrategyOptimizer 类，包含 analyze_all_sources、analyze_frequency、analyze_timeout、analyze_success_rate、analyze_quality 方法
    - 实现 apply_recommendation 方法（小幅调整直接应用，大幅调整生成 Change_Proposal）
    - 实现策略调整记录
    - 创建策略优化建议 Prompt 模板
    - _Requirements: 5.1-5.6_

  - [ ]* 11.2 编写策略自适应属性测试
    - **Property 13: 策略自适应触发正确性**
    - **Property 14: 重大策略变更审批要求**
    - **Property 15: 策略调整记录完整性**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

- [ ] 12. 检查点 - 所有进化服务完成
  - 确保概念漂移检测和策略自适应正常工作
  - 如有问题请询问用户

- [ ] 13. 后端 API 实现
  - [ ] 13.1 实现健康报告 API
    - 创建 `backend/app/api/health_report.py`
    - GET /api/health/report - 获取最新健康报告
    - GET /api/health/report/history - 获取历史健康报告列表
    - POST /api/health/detect - 手动触发健康检测
    - GET /api/health/pyramid/{pyramid_id} - 获取单个金字塔健康详情
    - GET /api/health/sources - 获取信息源健康汇总
    - GET /api/health/hotspots - 获取热点分布
    - _Requirements: 1.8, 6.1-6.8_

  - [ ] 13.2 实现热点管理 API
    - 创建 `backend/app/api/hotspots.py`
    - GET /api/hotspots - 获取热点列表
    - GET /api/hotspots/{id} - 获取热点详情
    - GET /api/hotspots/{id}/trajectory - 获取生命周期轨迹
    - PUT /api/hotspots/{id}/status - 手动调整热点状态
    - _Requirements: 3.7, 3.8_

  - [ ] 13.3 实现概念漂移 API
    - 创建 `backend/app/api/drift.py`
    - GET /api/drift/detections - 获取漂移检测结果
    - GET /api/drift/terms/{term}/history - 获取术语定义历史
    - POST /api/drift/detect - 手动触发漂移检测
    - _Requirements: 4.5, 4.6_

  - [ ] 13.4 实现策略调整 API
    - 创建 `backend/app/api/strategy.py`
    - GET /api/strategy/adjustments - 获取策略调整记录
    - GET /api/strategy/recommendations - 获取当前策略建议
    - _Requirements: 5.6_

  - [ ] 13.5 实现定时任务管理 API
    - 创建 `backend/app/api/scheduler.py`
    - GET /api/scheduler/tasks - 获取任务列表
    - GET /api/scheduler/tasks/{id} - 获取任务详情
    - POST /api/scheduler/tasks/{id}/trigger - 手动触发任务
    - PUT /api/scheduler/tasks/{id}/pause - 暂停任务
    - PUT /api/scheduler/tasks/{id}/resume - 恢复任务
    - GET /api/scheduler/executions - 获取执行历史
    - _Requirements: 7.4, 7.5, 7.7_

  - [ ] 13.6 实现系统配置 API
    - 创建 `backend/app/api/config.py`
    - GET /api/config - 获取所有配置
    - GET /api/config/{key} - 获取单个配置
    - PUT /api/config/{key} - 修改配置
    - GET /api/config/history - 获取配置变更历史
    - _Requirements: 8.4, 8.5, 8.7_

- [ ] 14. 注册定时任务
  - [ ] 14.1 注册所有定时任务到调度器
    - 在应用启动时注册以下任务：
      - 内容抓取任务（按信息源配置频率，复用迭代 2 抓取引擎）
      - 信息源健康检查（每小时，复用迭代 2 Health_Monitor）
      - 系统健康检测（每天，调用 HealthDetector.run_full_detection）
      - 热点生命周期更新（每天，调用 HotspotManager.update_lifecycle）
      - 概念漂移检测（每周，调用 ConceptDriftDetector.run_detection）
    - _Requirements: 7.1_

- [ ] 15. 检查点 - 后端 API 完成
  - 确保所有 API 端点正常工作
  - 使用 Swagger UI（/docs）手动验证端点
  - 如有问题请询问用户

- [ ] 16. 前端 API 客户端扩展
  - [ ] 16.1 扩展 API 客户端
    - 在 `frontend/src/lib/api.ts` 中添加健康报告、热点管理、概念漂移、策略调整、定时任务、系统配置相关的 API 调用方法
    - 在 `frontend/src/lib/types.ts` 中添加对应的类型定义
    - _Requirements: 所有前端相关需求_

- [ ] 17. 健康报告界面
  - [ ] 17.1 创建健康报告页面
    - 创建 `frontend/src/app/health/page.tsx`
    - 实现整体健康评分展示（大数字 + 健康等级标签）
    - 实现时间范围选择器（7天/30天/90天）
    - _Requirements: 6.1, 6.8_

  - [ ] 17.2 创建健康报告组件
    - 创建 `frontend/src/components/health/HealthOverview.tsx` - 整体评分和各维度评分
    - 创建 `frontend/src/components/health/PyramidHealthCard.tsx` - 金字塔健康度卡片和趋势图
    - 创建 `frontend/src/components/health/SourceHealthSummary.tsx` - 信息源健康汇总
    - 创建 `frontend/src/components/health/HotspotDistribution.tsx` - 热点分布饼图
    - 创建 `frontend/src/components/health/CrawlStats.tsx` - 抓取和校验统计
    - 创建 `frontend/src/components/health/ApprovalBacklog.tsx` - 审批积压情况
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ] 17.3 实现问题高亮和跳转
    - 实现健康问题高亮显示
    - 实现跳转到对应优化建议的链接
    - _Requirements: 6.7_

- [ ] 18. 定时任务管理界面
  - [ ] 18.1 创建任务管理页面
    - 创建 `frontend/src/app/tasks/page.tsx`
    - 创建 `frontend/src/components/tasks/TaskList.tsx` - 任务列表（名称、频率、状态、上次/下次执行时间）
    - 创建 `frontend/src/components/tasks/TaskDetail.tsx` - 任务详情和操作按钮（触发、暂停、恢复）
    - 创建 `frontend/src/components/tasks/ExecutionHistory.tsx` - 执行记录列表和成功率统计图
    - _Requirements: 9.1-9.5_

- [ ] 19. 系统配置界面
  - [ ] 19.1 创建配置管理页面
    - 创建 `frontend/src/app/settings/page.tsx`
    - 创建 `frontend/src/components/settings/ConfigForm.tsx` - 配置编辑表单（带验证和说明）
    - 创建 `frontend/src/components/settings/ConfigGroup.tsx` - 配置分组展示
    - 创建 `frontend/src/components/settings/ConfigHistory.tsx` - 配置变更历史
    - 实现敏感配置项脱敏显示
    - _Requirements: 10.1-10.5_

- [ ] 20. 导航栏更新
  - [ ] 20.1 更新导航栏
    - 在导航栏添加"健康报告"、"任务管理"、"系统配置"入口
    - _Requirements: 6.1, 9.1, 10.1_

- [ ] 21. 检查点 - 前端界面完成
  - 确保所有页面和交互正常
  - 确保前后端联调正常
  - 如有问题请询问用户

- [ ] 22. 集成测试
  - [ ] 22.1 编写健康检测集成测试
    - 测试完整健康检测流程（检测→报告生成→问题触发优化）
    - _Requirements: 1.1-1.9_

  - [ ] 22.2 编写热点生命周期集成测试
    - 测试完整生命周期流转（emerging→trending→mature→cooling→archived）
    - _Requirements: 3.1-3.8_

  - [ ] 22.3 编写策略自适应集成测试
    - 测试策略分析→建议生成→应用/审批流程
    - _Requirements: 5.1-5.6_

  - [ ] 22.4 编写定时任务集成测试
    - 测试任务注册→执行→重试→记录流程
    - _Requirements: 7.1-7.7_

- [ ] 23. 最终检查点 - 迭代 4 完成
  - 确保所有测试通过
  - 验证所有需求已实现
  - 验证所有正确性属性已测试
  - 如有问题请询问用户

## 注意事项

- 标记 `*` 的任务为可选测试任务，可根据时间情况跳过
- 每个检查点确保当前阶段的功能完整可用
- 属性测试使用 Hypothesis 库，每个测试运行至少 100 次迭代
- 测试标签格式：Feature: ai-radar-iteration-4, Property N: {property_text}
- 迭代 4 大量复用迭代 3 的 Change_Proposal 和审批系统，确保接口兼容
- 定时任务推荐使用 APScheduler 库实现
- 配置热更新通过内存缓存 + 文件监听实现
