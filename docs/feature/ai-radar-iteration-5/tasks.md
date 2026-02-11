# 实现计划：迭代 5 - 完善与 Docker 化

## 概述

本实现计划将迭代 5 的设计分解为可执行的编码任务。任务按照依赖关系排序，确保每个任务都建立在前一个任务的基础上。迭代 5 聚焦于系统完善（搜索、提示词管理、通知、导入导出）、性能优化（缓存、索引、速率限制）、监控和 Docker 容器化部署。

## 技术栈

- 后端：Python FastAPI
- 前端：Next.js + Tailwind CSS
- AI 服务：硅基流动 API
- 数据库：PostgreSQL
- 缓存：Redis（生产）/ 内存缓存（开发）
- 容器化：Docker + Docker Compose

## 任务列表

- [ ] 1. 数据模型扩展
  - [ ] 1.1 创建提示词相关数据模型
    - 创建 `backend/app/models/prompt_template.py`
    - 定义 PromptTemplate 模型，包含 id、scene、name、description、current_version_id 等字段
    - 创建 `backend/app/models/prompt_version.py`
    - 定义 PromptVersion 模型，包含 id、template_id、version、content、variables、call_count、avg_latency_ms、avg_quality_score、error_rate 等字段
    - 创建 `backend/app/models/ab_test.py`
    - 定义 ABTest 模型，包含 id、template_id、version_a_id、version_b_id、traffic_ratio、status、各版本调用统计 等字段
    - _Requirements: 2.1-2.6_

  - [ ] 1.2 创建通知相关数据模型
    - 创建 `backend/app/models/notification.py`
    - 定义 Notification 模型，包含 id、level、title、message、source_type、source_id、is_read、channels_sent、webhook_status 等字段
    - 创建 `backend/app/models/notification_preference.py`
    - 定义 NotificationPreference 模型，包含 id、in_app_enabled、webhook_enabled、webhook_url、min_level、quiet_hours 配置等字段
    - _Requirements: 4.1-4.9_

  - [ ] 1.3 创建监控相关数据模型
    - 创建 `backend/app/models/api_metric.py`
    - 定义 APIMetric 模型，包含 id、endpoint、method、status_code、response_time_ms 等字段
    - 创建 `backend/app/models/error_record.py`
    - 定义 ErrorRecord 模型，包含 id、error_type、error_message、stack_trace、context、source_service、retry_count、max_retries、is_resolved 等字段
    - _Requirements: 5.6, 9.1-9.6_

  - [ ] 1.4 创建数据库迁移脚本
    - 使用 Alembic 创建迁移脚本
    - 添加全文搜索索引（PostgreSQL pg_trgm 扩展）
    - 添加复合索引优化高频查询
    - 执行迁移创建新表和索引
    - _Requirements: 5.8_

- [ ] 2. 检查点 - 数据模型完成
  - 确保所有测试通过，如有问题请询问用户

- [ ] 3. 缓存服务
  - [ ] 3.1 实现缓存服务
    - 创建 `backend/app/services/cache/cache_service.py`
    - 实现 CacheService 类，支持 Redis 和内存缓存两种后端
    - 实现 get、set、delete、delete_pattern 方法
    - 实现 invalidate_pyramid、invalidate_search 缓存失效方法
    - 配置不同数据类型的 TTL（金字塔 5 分钟、搜索 1 分钟、指标 30 秒）
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 3.2 编写缓存属性测试
    - **Property 10: 缓存失效及时性**
    - **Validates: Requirements 5.3**

- [ ] 4. 中间件层
  - [ ] 4.1 实现速率限制中间件
    - 创建 `backend/app/middleware/rate_limiter.py`
    - 实现基于 IP 的滑动窗口速率限制
    - 支持不同端点类别的限制配置（默认 60/分钟、AI 相关 10/分钟、导出 5/5分钟）
    - 超限时返回 429 状态码和 Retry-After 头
    - 记录被限制的请求日志
    - _Requirements: 7.1-7.5_

  - [ ] 4.2 实现全局错误处理中间件
    - 创建 `backend/app/middleware/error_handler.py`
    - 实现不同错误类型的重试策略（网络快速重试、AI 指数退避、数据库不重试）
    - 实现熔断机制（5 分钟内同类错误超过 10 次触发熔断）
    - 实现错误记录和失败任务管理
    - _Requirements: 9.1-9.6_

  - [ ] 4.3 实现性能追踪中间件
    - 创建 `backend/app/middleware/performance_tracker.py`
    - 自动记录每个 API 请求的端点、方法、状态码、响应时间
    - 记录慢查询日志（响应时间超过 3 秒）
    - _Requirements: 5.6, 5.7_

  - [ ]* 4.4 编写中间件属性测试
    - **Property 11: 速率限制正确性**
    - **Property 12: 错误重试策略遵守**
    - **Property 13: 熔断机制触发正确性**
    - **Property 15: API 指标记录完整性**
    - **Validates: Requirements 7.1, 7.3, 9.1, 9.3, 9.4, 5.6**

- [ ] 5. 检查点 - 基础设施完成
  - 确保缓存服务和中间件正常工作
  - 如有问题请询问用户

- [ ] 6. 全文搜索服务
  - [ ] 6.1 实现全文搜索服务
    - 创建 `backend/app/services/search/search_service.py`
    - 实现 SearchService 类，包含 search、suggest、highlight、parse_boolean_query 方法
    - 实现布尔查询解析（AND/OR/NOT）
    - 实现多维度过滤（节点层级、时间范围、质量分数、验证状态）
    - 实现搜索结果排序（相关度、时间、质量分数）
    - 实现关键词高亮
    - 集成缓存服务（相同查询 1 分钟内返回缓存）
    - _Requirements: 1.1-1.8_

  - [ ]* 6.2 编写搜索属性测试
    - **Property 1: 搜索结果相关性**
    - **Property 2: 布尔搜索语义正确性**
    - **Property 3: 节点过滤层级完整性**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [ ] 7. 提示词管理服务
  - [ ] 7.1 实现提示词管理服务
    - 创建 `backend/app/services/prompt/prompt_manager.py`
    - 实现 PromptManager 类，包含模板管理、版本管理、测试、A/B 测试方法
    - 实现 get_prompt_for_scene 方法（支持 A/B 测试分流）
    - 实现 record_prompt_metrics 方法（记录效果指标）
    - 预置所有场景的默认提示词模板（从迭代 2-4 的 Prompt 模板迁移）
    - _Requirements: 2.1-2.6_

  - [ ]* 7.2 编写提示词管理属性测试
    - **Property 4: 提示词版本链完整性**
    - **Property 5: A/B 测试流量分配正确性**
    - **Validates: Requirements 2.2, 2.4**

- [ ] 8. 通知服务
  - [ ] 8.1 实现通知服务
    - 创建 `backend/app/services/notification/notification_service.py`
    - 实现 NotificationService 类，包含 send、list、mark_read、get_unread_count 方法
    - 实现通知级别过滤和静默时段检查
    - 创建 `backend/app/services/notification/channels/in_app.py` - 站内通知渠道
    - 创建 `backend/app/services/notification/channels/webhook.py` - Webhook 通知渠道
    - _Requirements: 4.1-4.9_

  - [ ] 8.2 集成通知触发点
    - 在审批队列管理器中集成新提案通知
    - 在信息源健康监测中集成异常告警通知
    - 在系统健康检测中集成问题报告通知
    - 在 AI 服务客户端中集成持续不可用告警
    - _Requirements: 4.1-4.4_

  - [ ]* 8.3 编写通知属性测试
    - **Property 8: 通知静默时段遵守**
    - **Property 9: 通知级别过滤正确性**
    - **Validates: Requirements 4.7, 4.8**

- [ ] 9. 数据导入导出服务
  - [ ] 9.1 实现数据导出服务
    - 创建 `backend/app/services/data/export_service.py`
    - 实现 ExportService 类，支持导出金字塔（含/不含内容）和信息源配置
    - 实现敏感信息脱敏（API 密钥、认证令牌）
    - 实现异步导出（大数据量时返回任务 ID）
    - _Requirements: 3.1-3.3, 3.8_

  - [ ] 9.2 实现数据导入服务
    - 创建 `backend/app/services/data/import_service.py`
    - 实现 ImportService 类，包含 validate、detect_conflicts、import_data 方法
    - 实现 JSON 格式验证和完整性检查
    - 实现冲突检测和三种解决方案（跳过、覆盖、重命名）
    - 实现 ID 映射（导入时生成新 ID 并维护关联关系）
    - _Requirements: 3.4-3.7_

  - [ ]* 9.3 编写导入导出属性测试
    - **Property 6: 导出导入往返一致性**
    - **Property 7: 导入冲突检测完整性**
    - **Property 14: 导出数据脱敏**
    - **Validates: Requirements 3.1, 3.3, 3.4, 3.6**

- [ ] 10. 监控指标收集服务
  - [ ] 10.1 实现监控指标收集器
    - 创建 `backend/app/services/monitoring/metrics_collector.py`
    - 实现业务指标收集（抓取数量、校验通过率、审批处理速度、用户贡献数量）
    - 创建 `backend/app/services/monitoring/performance_monitor.py`
    - 实现性能指标聚合（API 响应时间分布、P95、错误率）
    - 实现 AI 指标聚合（调用次数、耗时、Token 用量、成功率）
    - 实现系统资源指标收集（内存、CPU、磁盘）
    - _Requirements: 6.1-6.7_

- [ ] 11. 检查点 - 核心服务完成
  - 确保搜索、提示词管理、通知、导入导出、监控服务正常工作
  - 如有问题请询问用户

- [ ] 12. 后端 API 实现
  - [ ] 12.1 实现搜索 API
    - 创建 `backend/app/api/search.py`
    - GET /api/search - 全文搜索（支持关键词、布尔查询、多维度过滤、排序）
    - GET /api/search/suggest - 搜索建议
    - _Requirements: 1.1-1.8_

  - [ ] 12.2 实现提示词管理 API
    - 创建 `backend/app/api/prompts.py`
    - GET /api/prompts - 获取所有模板
    - GET /api/prompts/{id} - 获取模板详情
    - POST /api/prompts/{id}/versions - 创建新版本
    - PUT /api/prompts/{id}/active-version - 设置当前版本
    - POST /api/prompts/versions/{id}/test - 测试提示词
    - GET /api/prompts/{id}/versions - 获取版本历史
    - POST /api/prompts/{id}/ab-test - 启动 A/B 测试
    - PUT /api/prompts/ab-tests/{id}/stop - 停止 A/B 测试
    - GET /api/prompts/ab-tests/{id} - 获取 A/B 测试结果
    - _Requirements: 2.1-2.6_

  - [ ] 12.3 实现通知 API
    - 创建 `backend/app/api/notifications.py`
    - GET /api/notifications - 获取通知列表
    - GET /api/notifications/unread-count - 获取未读数量
    - PUT /api/notifications/{id}/read - 标记已读
    - PUT /api/notifications/read-all - 全部标记已读
    - GET /api/notifications/preferences - 获取通知偏好
    - PUT /api/notifications/preferences - 更新通知偏好
    - _Requirements: 4.5, 4.7, 4.8_

  - [ ] 12.4 实现数据导入导出 API
    - 创建 `backend/app/api/data_transfer.py`
    - POST /api/data/export - 导出数据（异步，返回任务 ID）
    - GET /api/data/export/{task_id} - 获取导出状态/下载
    - POST /api/data/import/validate - 验证导入数据
    - POST /api/data/import - 执行导入
    - _Requirements: 3.1-3.8_

  - [ ] 12.5 实现监控 API
    - 创建 `backend/app/api/monitoring.py`
    - GET /api/monitoring/snapshot - 获取性能快照
    - GET /api/monitoring/api-metrics - 获取 API 指标
    - GET /api/monitoring/ai-metrics - 获取 AI 指标
    - GET /api/monitoring/business-metrics - 获取业务指标
    - GET /api/monitoring/errors - 获取错误统计
    - GET /api/monitoring/errors/list - 获取错误列表
    - POST /api/monitoring/errors/{id}/retry - 手动重试失败任务
    - GET /api/monitoring/slow-queries - 获取慢查询日志
    - _Requirements: 6.1-6.7, 9.5, 9.6_

  - [ ] 12.6 注册中间件
    - 在 FastAPI 应用中注册速率限制中间件
    - 在 FastAPI 应用中注册性能追踪中间件
    - 在 FastAPI 应用中注册全局错误处理中间件
    - _Requirements: 7.1-7.5, 5.6, 9.1-9.4_

- [ ] 13. 检查点 - 后端 API 完成
  - 确保所有 API 端点正常工作
  - 使用 Swagger UI（/docs）手动验证端点
  - 如有问题请询问用户

- [ ] 14. 前端 API 客户端扩展
  - [ ] 14.1 扩展 API 客户端
    - 在 `frontend/src/lib/api.ts` 中添加搜索、提示词管理、通知、导入导出、监控相关的 API 调用方法
    - 在 `frontend/src/lib/types.ts` 中添加对应的类型定义
    - _Requirements: 所有前端相关需求_

- [ ] 15. 搜索界面
  - [ ] 15.1 创建搜索页面
    - 创建 `frontend/src/app/search/page.tsx`
    - 创建 `frontend/src/components/search/SearchBar.tsx` - 搜索输入框（含搜索建议下拉）
    - 创建 `frontend/src/components/search/SearchFilters.tsx` - 高级过滤面板（节点选择器、时间范围、质量分数滑块、验证状态多选）
    - 创建 `frontend/src/components/search/SearchResults.tsx` - 搜索结果列表（关键词高亮、无限滚动）
    - _Requirements: 10.1-10.6_

- [ ] 16. 提示词管理界面
  - [ ] 16.1 创建提示词管理页面
    - 创建 `frontend/src/app/prompts/page.tsx`
    - 创建 `frontend/src/components/prompts/PromptEditor.tsx` - 提示词编辑器（变量高亮、实时预览）
    - 创建 `frontend/src/components/prompts/PromptTester.tsx` - 测试面板（输入区域、结果展示）
    - 创建 `frontend/src/components/prompts/ABTestPanel.tsx` - A/B 测试面板（版本选择、流量配置、效果对比图表）
    - _Requirements: 11.1-11.5_

- [ ] 17. 监控仪表板界面
  - [ ] 17.1 创建监控页面
    - 创建 `frontend/src/app/monitor/page.tsx`
    - 创建 `frontend/src/components/monitor/SystemOverview.tsx` - 系统概览卡片（运行时间、总请求数、错误率）
    - 创建 `frontend/src/components/monitor/PerformanceCharts.tsx` - API 响应时间折线图和请求量柱状图
    - 创建 `frontend/src/components/monitor/AIMetrics.tsx` - AI 调用统计（次数、耗时、Token 用量）
    - 创建 `frontend/src/components/monitor/BusinessMetrics.tsx` - 业务指标趋势图
    - 创建 `frontend/src/components/monitor/ErrorLog.tsx` - 错误列表和趋势图
    - 实现自动刷新（默认 30 秒）
    - _Requirements: 12.1-12.6_

- [ ] 18. 数据管理界面
  - [ ] 18.1 创建数据管理页面
    - 创建 `frontend/src/app/data/page.tsx`
    - 创建 `frontend/src/components/data/ExportPanel.tsx` - 导出面板（选择导出范围、格式预览、下载）
    - 创建 `frontend/src/components/data/ImportPanel.tsx` - 导入面板（文件上传、验证结果、冲突解决、导入进度）
    - _Requirements: 3.1-3.8_

- [ ] 19. 通知组件
  - [ ] 19.1 创建通知组件
    - 创建 `frontend/src/components/common/NotificationBell.tsx` - 通知铃铛（未读数量徽章、下拉通知列表）
    - 在布局组件中集成通知铃铛
    - 在系统配置页面中添加通知偏好设置区域
    - _Requirements: 4.5, 13.4_

- [ ] 20. 导航栏完善
  - [ ] 20.1 更新导航栏
    - 添加"搜索"一级入口
    - 添加管理折叠菜单：健康报告、任务管理、系统配置、提示词管理、监控、数据管理
    - 在审批中心入口显示待审批数量徽章
    - 在右上角显示通知铃铛和未读数量
    - 实现响应式布局（移动端汉堡菜单）
    - _Requirements: 13.1-13.5_

- [ ] 21. 检查点 - 前端界面完成
  - 确保所有页面和交互正常
  - 确保前后端联调正常
  - 如有问题请询问用户

- [ ] 22. Docker 容器化
  - [ ] 22.1 创建后端 Dockerfile
    - 创建 `backend/Dockerfile`，基于 python:3.11-slim
    - 安装系统依赖（curl 用于健康检查）
    - 安装 Python 依赖
    - 配置启动命令（Alembic 迁移 + Uvicorn）
    - 创建 `backend/.dockerignore`
    - _Requirements: 8.1_

  - [ ] 22.2 创建前端 Dockerfile
    - 创建 `frontend/Dockerfile`，使用多阶段构建
    - 构建阶段：安装依赖、构建 Next.js
    - 运行阶段：使用 standalone 输出，最小化镜像
    - 创建 `frontend/.dockerignore`
    - _Requirements: 8.2_

  - [ ] 22.3 创建 Docker Compose 配置
    - 创建 `docker-compose.yml`，包含 backend、frontend、db（PostgreSQL 16）、redis（Redis 7）四个服务
    - 配置服务间依赖关系和健康检查
    - 配置数据卷持久化（db_data、redis_data、upload_data）
    - 配置环境变量通过 .env 文件管理
    - 创建 `.env.example` 环境变量模板
    - _Requirements: 8.3-8.7_

  - [ ] 22.4 创建开发环境 Docker Compose
    - 创建 `docker-compose.dev.yml`
    - 配置后端热重载（挂载源码目录）
    - 配置前端热重载
    - 暴露调试端口
    - _Requirements: 8.8_

- [ ] 23. 集成测试
  - [ ] 23.1 编写搜索集成测试
    - 测试全文搜索端到端流程（创建内容→搜索→验证结果高亮和排序）
    - 测试布尔查询（AND/OR/NOT）
    - 测试多维度过滤组合
    - _Requirements: 1.1-1.8_

  - [ ] 23.2 编写提示词管理集成测试
    - 测试版本创建→设置当前版本→测试提示词流程
    - 测试 A/B 测试完整流程（启动→记录指标→停止→查看结果）
    - _Requirements: 2.1-2.6_

  - [ ] 23.3 编写导入导出集成测试
    - 测试导出→导入往返一致性
    - 测试冲突检测和解决
    - 测试敏感信息脱敏
    - _Requirements: 3.1-3.8_

  - [ ] 23.4 编写通知集成测试
    - 测试通知触发→过滤→发送→记录流程
    - 测试静默时段和级别过滤
    - _Requirements: 4.1-4.9_

  - [ ] 23.5 编写性能和监控集成测试
    - 测试缓存命中和失效
    - 测试速率限制
    - 测试监控指标收集和查询
    - _Requirements: 5.1-5.8, 6.1-6.7, 7.1-7.5_

  - [ ] 23.6 编写 Docker 部署测试
    - 测试 docker-compose up 启动所有服务
    - 测试健康检查端点
    - 测试基本功能（创建金字塔、搜索内容）
    - _Requirements: 8.1-8.8_

- [ ] 24. 最终检查点 - 迭代 5 完成
  - 确保所有测试通过
  - 验证所有需求已实现
  - 验证所有正确性属性已测试
  - 验证 Docker 部署正常工作
  - 如有问题请询问用户

## 注意事项

- 标记 `*` 的任务为可选测试任务，可根据时间情况跳过
- 每个检查点确保当前阶段的功能完整可用
- 属性测试使用 Hypothesis 库，每个测试运行至少 100 次迭代
- 测试标签格式：Feature: ai-radar-iteration-5, Property N: {property_text}
- 缓存服务支持 Redis 和内存两种后端，开发环境使用内存缓存，生产环境使用 Redis
- 全文搜索使用 PostgreSQL 的 pg_trgm 扩展实现，不引入额外搜索引擎
- Docker 镜像构建应优化层缓存，减少构建时间
- 前端 Dockerfile 使用 Next.js standalone 输出模式，最小化生产镜像
- 速率限制使用 Redis 实现滑动窗口算法，开发环境可降级为内存实现
- 提示词管理需要将迭代 2-4 中硬编码的 Prompt 模板迁移到数据库管理
