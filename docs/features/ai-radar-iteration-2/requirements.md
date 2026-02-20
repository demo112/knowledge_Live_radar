# 需求文档 - 迭代 2：信息抓取

## 概述

本文档描述 AI Radar 系统迭代 2 的需求。迭代 2 的核心目标是实现动态信息源管理和内容抓取校验机制，使系统能够从多种来源自动获取、校验和处理 AI 领域的信息。

## 迭代目标

1. 实现动态信息源生命周期管理
2. 构建多类型抓取引擎（RSS、API、网页）
3. 实现三层校验机制（硬性、软性、交叉）
4. 集成硅基流动 AI 服务
5. 实现信息源健康监测
6. 实现信息源自动发现机制

## 依赖

- 迭代 1 完成的基础架构
- 迭代 1 完成的金字塔和节点数据模型
- 迭代 1 完成的信息源基础模型
- 迭代 1 完成的前端框架

## 需求

### 需求 1：信息源生命周期状态机

**用户故事：** 作为系统，我需要管理信息源的完整生命周期，以便自动维护信息源的质量和有效性。

#### 验收标准

1.1 WHEN 新信息源被创建 THEN Source_Lifecycle_Manager SHALL 将状态设置为 "discovered" 并创建验证任务
1.2 WHEN 信息源完成首次成功抓取 THEN Source_Lifecycle_Manager SHALL 将状态更新为 "verified"
1.3 WHEN 信息源连续 3 次抓取成功 THEN Source_Lifecycle_Manager SHALL 将状态更新为 "active"
1.4 WHEN 活跃信息源抓取失败率超过 30% THEN Source_Lifecycle_Manager SHALL 将状态更新为 "monitoring"
1.5 WHEN 监测中信息源恢复正常（连续 3 次成功）THEN Source_Lifecycle_Manager SHALL 将状态恢复为 "active"
1.6 WHEN 监测中信息源连续 7 天异常 THEN Source_Lifecycle_Manager SHALL 将状态更新为 "adjusting" 并生成 Change_Proposal
1.7 WHEN 信息源被标记为无效 THEN Source_Lifecycle_Manager SHALL 将状态更新为 "retired" 并停止所有抓取任务
1.8 THE Source_Lifecycle_Manager SHALL 记录每次状态变更的时间、原因、触发条件

### 需求 2：RSS 抓取器

**用户故事：** 作为系统，我需要能够抓取 RSS/Atom 格式的信息源，以便获取博客、新闻等内容。

#### 验收标准

2.1 WHEN 执行 RSS 抓取任务 THEN RSS_Fetcher SHALL 解析标准 RSS 2.0 和 Atom 1.0 格式
2.2 WHEN 解析 RSS 条目 THEN RSS_Fetcher SHALL 提取 title、link、description、pubDate、author 字段
2.3 WHEN RSS 源包含全文内容 THEN RSS_Fetcher SHALL 提取 content:encoded 或 content 字段
2.4 WHEN RSS 源返回非 200 状态码 THEN RSS_Fetcher SHALL 记录错误并标记抓取失败
2.5 WHEN RSS 源返回无效 XML THEN RSS_Fetcher SHALL 尝试容错解析并记录解析警告
2.6 THE RSS_Fetcher SHALL 支持配置请求超时时间（默认 30 秒）
2.7 THE RSS_Fetcher SHALL 支持配置 User-Agent 头
2.8 THE RSS_Fetcher SHALL 记录每次抓取的响应时间和条目数量

### 需求 3：API 抓取器

**用户故事：** 作为系统，我需要能够调用各类 API 获取信息，以便从 GitHub、HuggingFace 等平台获取数据。

#### 验收标准

3.1 WHEN 执行 API 抓取任务 THEN API_Fetcher SHALL 按配置发送 HTTP 请求（GET/POST）
3.2 WHEN API 需要认证 THEN API_Fetcher SHALL 支持 Bearer Token、API Key、Basic Auth 认证方式
3.3 WHEN API 返回 JSON 数据 THEN API_Fetcher SHALL 按配置的 JSONPath 表达式提取目标字段
3.4 WHEN API 返回分页数据 THEN API_Fetcher SHALL 按配置的分页规则自动翻页
3.5 WHEN API 返回速率限制错误（429）THEN API_Fetcher SHALL 等待指定时间后重试
3.6 THE API_Fetcher SHALL 支持配置请求头、查询参数、请求体
3.7 THE API_Fetcher SHALL 支持响应数据的字段映射配置
3.8 THE API_Fetcher SHALL 记录 API 调用的请求和响应详情（脱敏后）

### 需求 4：网页抓取器

**用户故事：** 作为系统，我需要能够抓取网页内容，以便从官方博客等没有 RSS 的站点获取信息。

#### 验收标准

4.1 WHEN 执行网页抓取任务 THEN Web_Fetcher SHALL 获取目标 URL 的 HTML 内容
4.2 WHEN 解析网页 THEN Web_Fetcher SHALL 支持 CSS 选择器和 XPath 表达式提取内容
4.3 WHEN 网页包含列表页 THEN Web_Fetcher SHALL 按配置提取所有条目链接
4.4 WHEN 需要抓取详情页 THEN Web_Fetcher SHALL 按配置的深度递归抓取
4.5 WHEN 网页需要 JavaScript 渲染 THEN Web_Fetcher SHALL 标记为不支持并记录警告
4.6 THE Web_Fetcher SHALL 遵守 robots.txt 规则
4.7 THE Web_Fetcher SHALL 对同一域名限制请求频率（默认 1 请求/秒）
4.8 THE Web_Fetcher SHALL 支持配置代理服务器

### 需求 5：抓取调度器

**用户故事：** 作为系统，我需要按计划调度抓取任务，以便定时更新内容。

#### 验收标准

5.1 WHEN 系统启动 THEN Crawl_Scheduler SHALL 加载所有活跃信息源的抓取配置
5.2 WHEN 到达信息源的抓取时间 THEN Crawl_Scheduler SHALL 创建抓取任务并加入队列
5.3 WHEN 抓取任务入队 THEN Crawl_Scheduler SHALL 按优先级排序（高优先级信息源优先）
5.4 WHEN 执行抓取任务 THEN Crawl_Scheduler SHALL 限制并发数量（默认最大 10 个并发）
5.5 WHEN 抓取任务完成 THEN Crawl_Scheduler SHALL 更新信息源的 last_crawled_at 和下次抓取时间
5.6 THE Crawl_Scheduler SHALL 支持手动触发单个信息源的即时抓取
5.7 THE Crawl_Scheduler SHALL 支持暂停和恢复全局抓取
5.8 THE Crawl_Scheduler SHALL 记录每个抓取任务的执行状态和耗时

### 需求 6：内容去重服务

**用户故事：** 作为系统，我需要识别重复内容，以便避免存储冗余信息。

#### 验收标准

6.1 WHEN 新内容进入系统 THEN Deduplication_Service SHALL 计算内容的 URL 指纹和内容指纹
6.2 WHEN URL 指纹完全匹配 THEN Deduplication_Service SHALL 标记为重复并跳过处理
6.3 WHEN 内容指纹相似度超过阈值（默认 90%）THEN Deduplication_Service SHALL 调用 AI 判断是否为更新版本
6.4 WHEN 确认为内容更新 THEN Deduplication_Service SHALL 更新原内容并记录版本历史
6.5 THE Deduplication_Service SHALL 使用 SimHash 算法计算内容指纹
6.6 THE Deduplication_Service SHALL 支持配置相似度阈值

### 需求 7：硬性校验器

**用户故事：** 作为系统，我需要对内容进行规则校验，以便过滤明显无效的内容。

#### 验收标准

7.1 WHEN 内容进入硬性校验 THEN Hard_Validator SHALL 验证原文 URL 的格式正确性
7.2 WHEN 内容进入硬性校验 THEN Hard_Validator SHALL 检查来源域名是否在白名单中
7.3 WHEN 内容包含 arXiv 链接 THEN Hard_Validator SHALL 验证 arXiv ID 格式（如 2401.12345）
7.4 WHEN 内容包含 GitHub 链接 THEN Hard_Validator SHALL 验证仓库路径格式（owner/repo）
7.5 WHEN 内容包含日期 THEN Hard_Validator SHALL 验证日期不超过当前时间且不早于 2020 年
7.6 WHEN 任一硬性校验失败 THEN Hard_Validator SHALL 返回失败原因列表并标记内容为 "hard_failed"
7.7 THE Hard_Validator SHALL 支持通过配置添加自定义校验规则
7.8 THE Hard_Validator SHALL 记录每条规则的执行结果

### 需求 8：软性校验器（AI 校验）

**用户故事：** 作为系统，我需要使用 AI 评估内容质量，以便筛选高质量信息。

#### 验收标准

8.1 WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用硅基流动 API 评估内容质量
8.2 WHEN 评估内容质量 THEN Soft_Validator SHALL 返回信息密度分数（0-100）
8.3 WHEN 评估内容质量 THEN Soft_Validator SHALL 返回标题内容一致性分数（0-100）
8.4 WHEN 评估内容质量 THEN Soft_Validator SHALL 返回是否为广告/营销内容的判断
8.5 WHEN 评估内容质量 THEN Soft_Validator SHALL 返回内容时效性评估
8.6 WHEN 综合质量分数低于阈值（默认 60）THEN Soft_Validator SHALL 标记内容为 "low_quality"
8.7 THE Soft_Validator SHALL 返回 AI 评估的详细理由
8.8 THE Soft_Validator SHALL 记录 AI 调用的输入输出和耗时

### 需求 9：交叉验证器

**用户故事：** 作为系统，我需要通过多源确认来验证信息可靠性。

#### 验收标准

9.1 WHEN 内容进入交叉验证 THEN Cross_Validator SHALL 搜索数据库中是否有相同主题的内容
9.2 WHEN 找到相关内容 THEN Cross_Validator SHALL 调用 AI 比较内容一致性
9.3 WHEN 多个独立源（>=2）确认相同信息 THEN Cross_Validator SHALL 标记为 "multi_source_confirmed"
9.4 WHEN 发现信息冲突 THEN Cross_Validator SHALL 标记为 "conflict" 并记录各源说法
9.5 WHEN 无法找到其他源确认 THEN Cross_Validator SHALL 标记为 "single_source"
9.6 THE Cross_Validator SHALL 记录交叉验证的详细过程

### 需求 10：AI 摘要生成服务

**用户故事：** 作为系统，我需要为内容生成摘要和标签，以便用户快速了解内容。

#### 验收标准

10.1 WHEN 内容通过校验 THEN AI_Summary_Service SHALL 调用硅基流动 API 生成 100-200 字摘要
10.2 WHEN 生成摘要 THEN AI_Summary_Service SHALL 提取 3-5 个关键标签
10.3 WHEN 生成摘要 THEN AI_Summary_Service SHALL 识别内容涉及的技术领域
10.4 WHEN AI 服务调用失败 THEN AI_Summary_Service SHALL 使用原文前 200 字作为临时摘要
10.5 THE AI_Summary_Service SHALL 支持配置摘要长度范围
10.6 THE AI_Summary_Service SHALL 记录生成的摘要和标签

### 需求 11：内容分类服务

**用户故事：** 作为系统，我需要将内容自动分类到金字塔节点，以便组织知识结构。

#### 验收标准

11.1 WHEN 内容完成摘要生成 THEN Content_Classifier SHALL 调用 AI 推荐最相关的金字塔节点
11.2 WHEN AI 推荐置信度高于阈值（默认 0.8）THEN Content_Classifier SHALL 自动分类到该节点
11.3 WHEN AI 推荐置信度低于阈值 THEN Content_Classifier SHALL 将内容加入人工分类队列
11.4 WHEN 内容可能属于多个节点 THEN Content_Classifier SHALL 支持多节点关联（最多 3 个）
11.5 THE Content_Classifier SHALL 记录分类决策的依据和置信度
11.6 THE Content_Classifier SHALL 支持人工调整分类结果

### 需求 12：信息源健康监测

**用户故事：** 作为系统管理员，我需要实时了解信息源的健康状态。

#### 验收标准

12.1 WHEN 系统执行健康检查 THEN Health_Monitor SHALL 检测每个活跃信息源的可达性
12.2 WHEN 系统执行健康检查 THEN Health_Monitor SHALL 计算过去 7 天的抓取成功率
12.3 WHEN 系统执行健康检查 THEN Health_Monitor SHALL 计算过去 7 天的平均响应时间
12.4 WHEN 系统执行健康检查 THEN Health_Monitor SHALL 计算过去 7 天的内容命中率（新内容/总抓取）
12.5 WHEN 健康指标异常 THEN Health_Monitor SHALL 更新信息源状态并生成告警
12.6 THE Health_Monitor SHALL 每小时执行一次健康检查
12.7 THE Health_Monitor SHALL 支持手动触发即时检查
12.8 THE Health_Monitor SHALL 计算综合健康度评分（0-100）

### 需求 13：信息源自动发现

**用户故事：** 作为系统，我需要从内容中自动发现新的潜在信息源。

#### 验收标准

13.1 WHEN 处理内容时发现外部链接 THEN Source_Discovery_Service SHALL 提取并记录链接域名
13.2 WHEN 同一域名出现次数超过阈值（默认 5 次）THEN Source_Discovery_Service SHALL 评估该域名
13.3 WHEN 域名评估通过 THEN Source_Discovery_Service SHALL 生成新信息源的 Change_Proposal
13.4 THE Source_Discovery_Service SHALL 维护已评估域名的记录，避免重复评估
13.5 THE Source_Discovery_Service SHALL 自动检测域名是否提供 RSS 订阅
13.6 THE Source_Discovery_Service SHALL 评估域名的权威性（官方域名优先）

### 需求 14：域名白名单管理

**用户故事：** 作为管理员，我需要管理可信域名白名单。

#### 验收标准

14.1 WHEN 管理员添加域名 THEN Whitelist_Manager SHALL 创建包含域名、可信等级、添加原因的记录
14.2 WHEN 管理员移除域名 THEN Whitelist_Manager SHALL 软删除并记录移除原因
14.3 THE Whitelist_Manager SHALL 预置权威域名（arxiv.org, github.com, openai.com, anthropic.com, huggingface.co 等）
14.4 THE Whitelist_Manager SHALL 支持域名通配符（如 *.openai.com）
14.5 THE Whitelist_Manager SHALL 提供域名查询 API

### 需求 15：硅基流动 API 客户端

**用户故事：** 作为系统，我需要集成硅基流动 API 来实现 AI 功能。

#### 验收标准

15.1 THE SiliconFlow_Client SHALL 支持调用 chat/completions 接口
15.2 THE SiliconFlow_Client SHALL 支持配置模型名称（默认 deepseek-chat）
15.3 THE SiliconFlow_Client SHALL 支持配置 temperature、max_tokens 等参数
15.4 WHEN API 调用失败 THEN SiliconFlow_Client SHALL 实现指数退避重试（最多 3 次）
15.5 WHEN API 持续不可用 THEN SiliconFlow_Client SHALL 将任务加入待处理队列
15.6 THE SiliconFlow_Client SHALL 记录所有 API 调用的耗时和 token 使用量
15.7 THE SiliconFlow_Client SHALL 支持通过环境变量配置 API Key

### 需求 16：抓取任务记录

**用户故事：** 作为管理员，我需要查看抓取任务的执行历史。

#### 验收标准

16.1 WHEN 抓取任务开始 THEN Crawl_Job_Recorder SHALL 创建任务记录（source_id, started_at, status=running）
16.2 WHEN 抓取任务完成 THEN Crawl_Job_Recorder SHALL 更新记录（ended_at, status, items_count, error_message）
16.3 THE Crawl_Job_Recorder SHALL 记录每次抓取的新增内容数量
16.4 THE Crawl_Job_Recorder SHALL 记录每次抓取的重复内容数量
16.5 THE Crawl_Job_Recorder SHALL 支持按信息源、时间范围、状态查询任务历史
16.6 THE Crawl_Job_Recorder SHALL 自动清理 30 天前的任务记录

### 需求 17：信息源配置模板

**用户故事：** 作为管理员，我需要使用模板快速配置常见信息源。

#### 验收标准

17.1 THE Source_Template_Service SHALL 提供 arXiv RSS 配置模板
17.2 THE Source_Template_Service SHALL 提供 GitHub Trending 配置模板
17.3 THE Source_Template_Service SHALL 提供 HuggingFace Daily Papers 配置模板
17.4 THE Source_Template_Service SHALL 提供通用博客 RSS 配置模板
17.5 WHEN 管理员选择模板 THEN Source_Template_Service SHALL 预填充配置字段
17.6 THE Source_Template_Service SHALL 支持保存自定义模板

### 需求 18：信息源管理界面增强

**用户故事：** 作为管理员，我需要通过界面管理信息源的完整生命周期。

#### 验收标准

18.1 WHEN 管理员查看信息源列表 THEN Source_Management_View SHALL 显示生命周期状态和健康度
18.2 WHEN 管理员查看信息源详情 THEN Source_Management_View SHALL 显示最近 10 次抓取记录
18.3 WHEN 管理员查看信息源详情 THEN Source_Management_View SHALL 显示健康度趋势图（7 天）
18.4 WHEN 管理员测试信息源 THEN Source_Management_View SHALL 显示测试抓取的详细结果
18.5 THE Source_Management_View SHALL 支持按生命周期状态筛选
18.6 THE Source_Management_View SHALL 显示信息源的关联节点

### 需求 19：内容列表增强

**用户故事：** 作为用户，我需要查看内容的校验状态和来源信息。

#### 验收标准

19.1 WHEN 用户查看内容列表 THEN Feed_View SHALL 显示校验状态标识（已验证/单源/待验证）
19.2 WHEN 用户查看内容列表 THEN Feed_View SHALL 显示内容质量分数
19.3 WHEN 用户查看内容详情 THEN Feed_View SHALL 显示完整校验报告
19.4 WHEN 用户查看内容详情 THEN Feed_View SHALL 显示来源信息源的名称和可信度
19.5 THE Feed_View SHALL 支持按校验状态筛选内容
19.6 THE Feed_View SHALL 支持按质量分数排序

### 需求 20：抓取统计仪表板

**用户故事：** 作为管理员，我需要查看抓取系统的整体运行状态。

#### 验收标准

20.1 WHEN 管理员访问仪表板 THEN Dashboard SHALL 显示今日抓取任务数量和成功率
20.2 WHEN 管理员访问仪表板 THEN Dashboard SHALL 显示今日新增内容数量
20.3 WHEN 管理员访问仪表板 THEN Dashboard SHALL 显示各状态信息源数量分布
20.4 WHEN 管理员访问仪表板 THEN Dashboard SHALL 显示校验通过率统计
20.5 WHEN 管理员访问仪表板 THEN Dashboard SHALL 显示 AI 服务调用统计
20.6 THE Dashboard SHALL 支持选择时间范围（今日/7天/30天）
