# 需求文档 - 迭代 5：完善与 Docker 化

## 概述

本文档描述 AI Radar 系统迭代 5 的需求。迭代 5 是最终迭代，核心目标是完善系统功能、优化性能、增强监控能力，并实现容器化部署，使系统达到生产就绪状态。

## 迭代目标

1. 实现全文搜索与高级过滤系统
2. 构建 AI 提示词管理与 A/B 测试机制
3. 实现数据导入导出功能
4. 完善通知系统（多渠道、静默时段）
5. 实现性能优化（缓存、异步处理、查询优化）
6. 构建系统监控仪表板（性能指标、业务指标）
7. 实现 Docker 容器化部署
8. 完善错误处理与恢复机制

## 依赖

- 迭代 1 完成的基础架构（金字塔、节点、信息源、内容数据模型、前端框架）
- 迭代 2 完成的信息抓取系统（抓取引擎、校验机制、AI 服务集成）
- 迭代 3 完成的变更提案系统（Change_Proposal、审批队列、影响分析、快照/回滚）
- 迭代 4 完成的自我进化系统（健康检测、重构建议、热点管理、定时任务、配置管理）

## 术语表

- **Full_Text_Search（全文搜索）**: 在内容标题、摘要、标签中进行关键词搜索的能力
- **Prompt_Template（提示词模板）**: AI 服务调用时使用的结构化提示词
- **A/B_Test（A/B 测试）**: 同时运行两个版本的提示词并比较效果
- **Cache_Layer（缓存层）**: 用于加速频繁查询的内存缓存
- **Monitoring_Dashboard（监控仪表板）**: 展示系统性能和业务指标的可视化界面
- **Container（容器）**: Docker 容器化的应用实例
- **Rate_Limiter（速率限制器）**: 限制 API 请求频率的中间件

## 需求

### 需求 1：全文搜索系统

**用户故事：** 作为用户，我希望能够快速搜索和过滤内容，以便精准找到需要的信息。

#### 验收标准

1.1 WHEN 用户执行全文搜索 THEN Search_Service SHALL 在内容标题、摘要、标签中搜索关键词并返回匹配结果
1.2 WHEN 用户执行高级搜索 THEN Search_Service SHALL 支持布尔运算符（AND、OR、NOT）组合查询
1.3 WHEN 用户按金字塔节点过滤 THEN Search_Service SHALL 返回该节点及其所有子节点下的内容
1.4 WHEN 用户按时间范围过滤 THEN Search_Service SHALL 返回指定时间范围内的内容
1.5 WHEN 用户按质量分数过滤 THEN Search_Service SHALL 返回分数高于指定阈值的内容
1.6 WHEN 用户按验证状态过滤 THEN Search_Service SHALL 返回指定验证状态（multi_source_confirmed/single_source/conflict/pending）的内容
1.7 THE Search_Service SHALL 支持搜索结果排序（相关度、时间、质量分数）
1.8 THE Search_Service SHALL 在搜索结果中高亮显示匹配的关键词

### 需求 2：AI 提示词管理

**用户故事：** 作为管理员，我希望能够管理和优化 AI 服务使用的提示词模板，以便持续提升 AI 输出质量。

#### 验收标准

2.1 THE Prompt_Manager SHALL 维护以下场景的提示词模板：内容质量评估、摘要生成、概念提取、分类推荐、变更建议生成、金字塔结构分析、概念漂移检测、策略优化建议
2.2 WHEN 管理员编辑提示词 THEN Prompt_Manager SHALL 保存新版本并保留所有历史版本
2.3 WHEN 管理员测试提示词 THEN Prompt_Manager SHALL 使用指定的测试输入调用 AI 服务并返回结果
2.4 WHEN 管理员启动 A/B 测试 THEN Prompt_Manager SHALL 按配置的流量比例将请求分配到两个版本
2.5 WHEN A/B 测试运行中 THEN Prompt_Manager SHALL 记录每个版本的调用次数、平均耗时、输出质量评分
2.6 THE Prompt_Manager SHALL 记录各版本提示词的效果指标（平均质量分数、平均耗时、错误率）

### 需求 3：数据导入导出

**用户故事：** 作为管理员，我希望能够导入导出系统数据，以便进行数据迁移、备份和恢复。

#### 验收标准

3.1 WHEN 管理员导出金字塔 THEN Export_Service SHALL 生成包含完整结构（节点层级、关联关系）的 JSON 文件
3.2 WHEN 管理员导出金字塔含内容 THEN Export_Service SHALL 在 JSON 中包含各节点关联的内容条目
3.3 WHEN 管理员导出信息源配置 THEN Export_Service SHALL 生成包含所有信息源配置（脱敏后）的 JSON 文件
3.4 WHEN 管理员导入金字塔 THEN Import_Service SHALL 解析 JSON 并创建金字塔结构，自动处理 ID 映射
3.5 WHEN 管理员导入信息源配置 THEN Import_Service SHALL 解析 JSON 并创建信息源记录
3.6 IF 导入数据与现有数据冲突（名称重复）THEN Import_Service SHALL 提示冲突并提供跳过、覆盖、重命名三种解决选项
3.7 THE Import_Service SHALL 在导入前验证 JSON 数据的格式和完整性
3.8 THE Export_Service SHALL 支持选择性导出（仅结构/包含内容/包含信息源配置）

### 需求 4：通知系统完善

**用户故事：** 作为管理员，我希望通过多种渠道收到重要事件的通知，并能配置通知偏好，以便及时响应而不被打扰。

#### 验收标准

4.1 WHEN 新提案加入审批队列 THEN Notification_Service SHALL 发送新提案通知
4.2 WHEN 信息源健康状态变为异常 THEN Notification_Service SHALL 发送告警通知
4.3 WHEN 系统健康检测发现问题 THEN Notification_Service SHALL 发送健康报告通知
4.4 WHEN AI 服务持续不可用（连续 3 次失败）THEN Notification_Service SHALL 发送紧急告警
4.5 THE Notification_Service SHALL 支持站内通知（系统内消息列表）
4.6 THE Notification_Service SHALL 支持 Webhook 通知（可配置 URL）
4.7 THE Notification_Service SHALL 支持通知级别配置（信息、警告、紧急）
4.8 THE Notification_Service SHALL 支持通知静默时段设置（如 22:00-08:00 不发送非紧急通知）
4.9 THE Notification_Service SHALL 记录所有通知的发送历史和送达状态

### 需求 5：性能优化

**用户故事：** 作为系统，我需要保持良好的性能，以便在数据量增长时仍能提供流畅的用户体验。

#### 验收标准

5.1 THE Cache_Service SHALL 对金字塔可视化数据实现 Redis/内存缓存，TTL 为 5 分钟
5.2 THE Cache_Service SHALL 对搜索结果实现缓存，相同查询条件在 1 分钟内返回缓存结果
5.3 WHEN 金字塔结构或内容发生变更 THEN Cache_Service SHALL 自动失效相关缓存
5.4 THE API_Service SHALL 对所有列表接口实现游标分页，单页最大 100 条
5.5 THE API_Service SHALL 对大量数据的操作（批量导入、全量健康检测）实现异步处理并返回任务 ID
5.6 THE Performance_Monitor SHALL 监控所有 API 端点的响应时间，P95 响应时间不超过 2 秒
5.7 THE Performance_Monitor SHALL 在 API 响应时间超过阈值（默认 3 秒）时记录慢查询日志
5.8 THE Database_Service SHALL 对高频查询添加复合索引（内容按节点+时间、信息源按状态+健康度）

### 需求 6：系统监控仪表板

**用户故事：** 作为管理员，我希望通过监控仪表板查看系统运行状态和关键指标，以便及时发现和解决问题。

#### 验收标准

6.1 WHEN 管理员访问监控页面 THEN Monitoring_Dashboard SHALL 展示系统性能指标：API 平均响应时间、P95 响应时间、请求总量
6.2 WHEN 管理员访问监控页面 THEN Monitoring_Dashboard SHALL 展示数据库指标：查询耗时分布、连接池使用率
6.3 WHEN 管理员访问监控页面 THEN Monitoring_Dashboard SHALL 展示 AI 服务指标：调用次数、平均耗时、成功率、Token 使用量
6.4 WHEN 管理员访问监控页面 THEN Monitoring_Dashboard SHALL 展示业务指标：今日抓取数量、校验通过率、审批处理速度、用户贡献数量
6.5 WHEN 管理员访问监控页面 THEN Monitoring_Dashboard SHALL 展示系统资源：内存使用、CPU 使用、磁盘空间
6.6 THE Monitoring_Dashboard SHALL 支持选择时间范围（1小时/6小时/24小时/7天）
6.7 THE Monitoring_Dashboard SHALL 对异常指标进行红色高亮标记

### 需求 7：API 速率限制

**用户故事：** 作为系统，我需要限制 API 请求频率，以便防止滥用和保护系统稳定性。

#### 验收标准

7.1 THE Rate_Limiter SHALL 对公开 API 实现速率限制（默认 60 请求/分钟/IP）
7.2 THE Rate_Limiter SHALL 对 AI 相关 API 实现更严格的速率限制（默认 10 请求/分钟/IP）
7.3 WHEN 请求超过速率限制 THEN Rate_Limiter SHALL 返回 429 状态码和 Retry-After 头
7.4 THE Rate_Limiter SHALL 支持通过配置调整各端点的速率限制
7.5 THE Rate_Limiter SHALL 记录被限制的请求日志

### 需求 8：Docker 容器化部署

**用户故事：** 作为运维人员，我希望能够通过 Docker 一键部署整个系统，以便简化部署流程和环境管理。

#### 验收标准

8.1 THE Docker_Config SHALL 提供后端服务的 Dockerfile，基于 Python 3.11+ 镜像
8.2 THE Docker_Config SHALL 提供前端服务的 Dockerfile，使用多阶段构建优化镜像大小
8.3 THE Docker_Config SHALL 提供 docker-compose.yml，包含以下服务：backend（FastAPI）、frontend（Next.js）、db（PostgreSQL）、redis（缓存）
8.4 THE Docker_Config SHALL 通过 .env 文件管理环境变量（数据库连接、API 密钥、服务端口等）
8.5 THE Docker_Config SHALL 配置数据卷持久化数据库数据和上传文件
8.6 THE Docker_Config SHALL 配置服务间网络隔离（前端只能访问后端，后端可访问数据库和 Redis）
8.7 THE Docker_Config SHALL 配置健康检查（health check）确保服务正常启动
8.8 THE Docker_Config SHALL 提供 docker-compose.dev.yml 用于开发环境（热重载、调试端口）

### 需求 9：错误处理完善

**用户故事：** 作为系统，我需要优雅地处理各类错误并支持恢复，以便保持系统稳定运行。

#### 验收标准

9.1 WHEN 后台任务发生错误 THEN Error_Handler SHALL 记录错误详情并按配置的重试策略自动重试
9.2 WHEN AI 服务调用失败 THEN Error_Handler SHALL 将任务加入重试队列，并在重试耗尽后通知管理员
9.3 THE Error_Handler SHALL 对不同类型的错误采用不同的重试策略：网络错误（快速重试 3 次）、AI 服务限流（指数退避）、数据库错误（不重试，立即告警）
9.4 THE Error_Handler SHALL 在错误持续发生（同类错误 5 分钟内超过 10 次）时触发熔断机制
9.5 THE Error_Handler SHALL 支持管理员通过界面查看失败任务列表并手动重试
9.6 THE Error_Handler SHALL 提供错误统计 API（按类型、时间范围统计错误数量和趋势）

### 需求 10：搜索界面

**用户故事：** 作为用户，我希望通过直观的搜索界面快速找到需要的内容。

#### 验收标准

10.1 WHEN 用户访问搜索页面 THEN Search_View SHALL 展示搜索输入框和高级过滤面板
10.2 WHEN 用户输入搜索词 THEN Search_View SHALL 实时显示搜索建议（基于历史搜索和热门标签）
10.3 WHEN 搜索结果返回 THEN Search_View SHALL 高亮显示匹配关键词并展示结果列表
10.4 WHEN 用户展开高级过滤 THEN Search_View SHALL 提供金字塔节点选择器、时间范围选择器、质量分数滑块、验证状态多选
10.5 THE Search_View SHALL 显示搜索结果总数和当前排序方式
10.6 THE Search_View SHALL 支持搜索结果的无限滚动加载

### 需求 11：提示词管理界面

**用户故事：** 作为管理员，我希望通过界面管理 AI 提示词模板，以便方便地优化和测试提示词。

#### 验收标准

11.1 WHEN 管理员访问提示词管理页面 THEN Prompt_View SHALL 展示所有提示词模板列表，按场景分组
11.2 WHEN 管理员编辑提示词 THEN Prompt_View SHALL 提供代码编辑器（支持变量高亮）和实时预览
11.3 WHEN 管理员测试提示词 THEN Prompt_View SHALL 提供测试输入区域和结果展示区域
11.4 WHEN 管理员查看版本历史 THEN Prompt_View SHALL 展示版本列表和版本间差异对比
11.5 WHEN 管理员配置 A/B 测试 THEN Prompt_View SHALL 提供版本选择、流量比例配置和效果对比图表

### 需求 12：监控仪表板界面

**用户故事：** 作为管理员，我希望通过可视化仪表板监控系统运行状态。

#### 验收标准

12.1 WHEN 管理员访问监控页面 THEN Monitor_View SHALL 展示系统概览卡片（运行时间、总请求数、错误率）
12.2 WHEN 管理员查看性能指标 THEN Monitor_View SHALL 展示 API 响应时间折线图和请求量柱状图
12.3 WHEN 管理员查看 AI 指标 THEN Monitor_View SHALL 展示 AI 调用统计（次数、耗时、Token 用量）
12.4 WHEN 管理员查看业务指标 THEN Monitor_View SHALL 展示抓取统计、校验统计、审批统计的趋势图
12.5 WHEN 管理员查看错误日志 THEN Monitor_View SHALL 展示最近错误列表和错误趋势图
12.6 THE Monitor_View SHALL 支持自动刷新（默认 30 秒）

### 需求 13：导航栏与布局完善

**用户故事：** 作为用户，我希望通过清晰的导航快速访问系统各功能模块。

#### 验收标准

13.1 THE Navigation SHALL 包含以下一级入口：信息流、金字塔、信息源、审批中心、搜索
13.2 THE Navigation SHALL 包含以下管理入口（折叠菜单）：健康报告、任务管理、系统配置、提示词管理、监控、数据管理
13.3 THE Navigation SHALL 在审批中心入口显示待审批数量徽章
13.4 THE Navigation SHALL 在右上角显示通知图标和未读通知数量
13.5 THE Navigation SHALL 支持响应式布局，在移动端显示为汉堡菜单
