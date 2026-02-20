# 需求文档 - 迭代 4：自我进化

## 概述

本文档描述 AI Radar 系统迭代 4 的需求。迭代 4 的核心目标是实现系统的自我进化能力，包括系统健康检测、金字塔重构建议、热点生命周期管理、概念漂移检测、抓取策略自适应、健康报告界面、定时任务管理和系统配置管理。

## 迭代目标

1. 实现系统全面健康检测机制
2. 构建金字塔结构重构建议引擎
3. 实现热点话题生命周期自动管理
4. 构建概念漂移检测与术语更新机制
5. 实现抓取策略自适应优化
6. 构建健康报告可视化界面
7. 实现定时任务统一调度管理
8. 实现系统配置热更新管理

## 依赖

- 迭代 1 完成的基础架构（金字塔、节点、信息源、内容数据模型）
- 迭代 2 完成的信息抓取系统（抓取引擎、校验机制、AI 服务集成、信息源健康监测）
- 迭代 3 完成的变更提案系统（Change_Proposal、审批队列、影响分析、决策执行、快照/回滚）

## 术语表

- **Health_Detection（健康检测）**: 对系统各维度进行全面评估的周期性任务
- **Health_Report（健康报告）**: 健康检测生成的综合评估报告
- **Restructure_Proposal（重构提案）**: AI 基于结构分析生成的金字塔重构建议
- **Hotspot（热点话题）**: 当前关注度高的话题，具有生命周期状态
- **Hotspot_Lifecycle（热点生命周期）**: 热点的状态流转：新兴→热门→成熟→冷却→归档
- **Concept_Drift（概念漂移）**: 术语或概念含义随时间发生的变化
- **Strategy_Adaptation（策略自适应）**: 系统根据运行数据自动调整抓取策略的能力
- **Scheduled_Task（定时任务）**: 系统周期性执行的自动化任务
- **Hot_Reload（热更新）**: 配置变更后无需重启即可生效的能力

## 需求

### 需求 1：系统健康检测

**用户故事：** 作为系统，我需要持续监测自身健康状态，以便发现需要优化的问题并触发相应的自我进化流程。

#### 验收标准

1.1 WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估每个金字塔的结构平衡性并返回 0-100 的评分
1.2 WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估所有信息源的整体健康状况并返回 0-100 的评分
1.3 WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估热点话题的生命周期分布并返回分布统计
1.4 WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估内容更新频率和覆盖度并返回 0-100 的评分
1.5 WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估审批队列的积压情况并返回积压数量和平均等待时间
1.6 WHEN 检测到健康问题 THEN Health_Detector SHALL 生成问题报告并触发相应的优化流程（重构建议、策略调整等）
1.7 THE Health_Detector SHALL 每天执行一次全面健康检测
1.8 THE Health_Detector SHALL 支持手动触发即时检测
1.9 THE Health_Detector SHALL 计算系统整体健康评分（各维度加权平均，0-100）

### 需求 2：金字塔重构建议

**用户故事：** 作为系统，我需要能够识别金字塔结构问题并生成重构建议，以便优化知识组织结构。

#### 验收标准

2.1 WHEN 检测到节点关联内容数量超过阈值（默认 50）THEN Restructure_Advisor SHALL 生成节点拆分的 Change_Proposal，包含拆分方案和内容重分配建议
2.2 WHEN 检测到节点连续 30 天无新增内容 THEN Restructure_Advisor SHALL 生成节点删除或合并的 Change_Proposal
2.3 WHEN 检测到金字塔层级深度超过阈值（默认 5 层）THEN Restructure_Advisor SHALL 生成层级扁平化的 Change_Proposal
2.4 WHEN 检测到同级节点数量超过阈值（默认 10 个）THEN Restructure_Advisor SHALL 生成节点分组的 Change_Proposal
2.5 WHEN 检测到节点命名风格不一致 THEN Restructure_Advisor SHALL 生成重命名的 Change_Proposal
2.6 THE Restructure_Advisor SHALL 在每个提案中包含重构理由、预期效果和风险评估
2.7 THE Restructure_Advisor SHALL 支持通过配置调整各项重构触发阈值

### 需求 3：热点生命周期管理

**用户故事：** 作为系统，我需要追踪热点话题的生命周期，以便合理调整内容展示优先级和资源分配。

#### 验收标准

3.1 WHEN 新话题在 7 天内出现频率超过阈值（默认 5 次）THEN Hotspot_Manager SHALL 将该话题标记为"新兴"状态
3.2 WHEN 新兴热点在后续 7 天内提及频率持续增长 THEN Hotspot_Manager SHALL 将状态更新为"热门"
3.3 WHEN 热门话题提及频率增长放缓（增长率低于 10%）THEN Hotspot_Manager SHALL 将状态更新为"成熟"
3.4 WHEN 成熟话题提及频率连续 14 天下降 THEN Hotspot_Manager SHALL 将状态更新为"冷却"
3.5 WHEN 冷却话题连续 30 天无新增内容 THEN Hotspot_Manager SHALL 将状态更新为"归档"
3.6 WHEN 热点状态变化 THEN Hotspot_Manager SHALL 调整相关内容的展示优先级权重
3.7 THE Hotspot_Manager SHALL 记录每个热点的完整生命周期轨迹，包含每次状态变更的时间和触发条件
3.8 THE Hotspot_Manager SHALL 支持管理员手动调整热点状态

### 需求 4：概念漂移检测

**用户故事：** 作为系统，我需要检测术语含义的变化，以便保持知识库的准确性和时效性。

#### 验收标准

4.1 WHEN 系统处理新内容 THEN Concept_Drift_Detector SHALL 提取关键术语的使用上下文并与历史上下文进行比较
4.2 WHEN 术语使用上下文的语义相似度低于阈值（默认 0.7）THEN Concept_Drift_Detector SHALL 标记为潜在概念漂移
4.3 WHEN 检测到概念漂移 THEN Concept_Drift_Detector SHALL 生成术语定义更新的 Change_Proposal，包含旧定义、新定义和漂移证据
4.4 WHEN 检测到概念漂移 THEN Concept_Drift_Detector SHALL 建议更新相关金字塔节点的描述
4.5 THE Concept_Drift_Detector SHALL 维护每个关键术语的历史定义版本列表
4.6 THE Concept_Drift_Detector SHALL 在检测报告中包含漂移证据（上下文变化示例）和建议更新内容

### 需求 5：抓取策略自适应

**用户故事：** 作为系统，我需要根据抓取效果自动调整策略，以便优化信息获取效率和质量。

#### 验收标准

5.1 WHEN 信息源实际更新频率与配置频率偏差超过 30% THEN Strategy_Optimizer SHALL 调整该源的抓取频率以匹配实际更新模式
5.2 WHEN 信息源平均响应时间超过配置超时时间的 80% THEN Strategy_Optimizer SHALL 增加超时时间和重试次数
5.3 WHEN 信息源抓取成功率连续 3 天低于 70% THEN Strategy_Optimizer SHALL 分析失败原因并调整抓取策略
5.4 WHEN 信息源内容质量分数连续 7 天平均低于 50 THEN Strategy_Optimizer SHALL 调整内容过滤规则
5.5 WHEN 策略调整幅度超过原配置的 50% THEN Strategy_Optimizer SHALL 生成 Change_Proposal 供人工审批
5.6 THE Strategy_Optimizer SHALL 记录每次策略调整的原因、调整前后参数和预期效果

### 需求 6：健康报告界面

**用户故事：** 作为管理员，我希望能够通过可视化界面查看系统健康报告，以便全面了解系统状态和问题。

#### 验收标准

6.1 WHEN 管理员访问健康报告页面 THEN Health_Report_View SHALL 展示系统整体健康评分（0-100）和健康等级
6.2 WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示各金字塔的健康度评分和近 30 天趋势图
6.3 WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示信息源健康状况汇总（各状态数量分布）
6.4 WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示热点话题生命周期分布饼图
6.5 WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示内容抓取和校验的统计数据（成功率、新增数量）
6.6 WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示审批队列积压情况（待审批数量、平均等待时间）
6.7 WHEN 存在健康问题 THEN Health_Report_View SHALL 高亮显示问题项并提供跳转到对应优化建议的链接
6.8 THE Health_Report_View SHALL 支持选择时间范围（7天/30天/90天）查看历史数据

### 需求 7：定时任务管理

**用户故事：** 作为系统，我需要统一管理各种定时任务，以便自动化执行周期性工作并保证任务可靠执行。

#### 验收标准

7.1 THE Scheduler_Service SHALL 管理以下定时任务：内容抓取（按信息源配置频率）、信息源健康检查（每小时）、系统健康检测（每天）、热点生命周期更新（每天）、概念漂移检测（每周）
7.2 WHEN 定时任务执行 THEN Scheduler_Service SHALL 记录执行开始时间、结束时间、执行结果和错误信息
7.3 WHEN 定时任务失败 THEN Scheduler_Service SHALL 按配置的重试策略进行重试（默认最多 3 次，指数退避）
7.4 THE Scheduler_Service SHALL 支持管理员手动触发任意任务的即时执行
7.5 THE Scheduler_Service SHALL 支持管理员暂停和恢复指定任务
7.6 THE Scheduler_Service SHALL 防止同一任务的并发执行（使用分布式锁或任务状态检查）
7.7 THE Scheduler_Service SHALL 提供任务执行历史查询 API，支持按任务类型和时间范围筛选

### 需求 8：系统配置管理

**用户故事：** 作为管理员，我希望能够灵活配置系统的各项参数，以便根据实际运行情况调整系统行为。

#### 验收标准

8.1 THE Configuration_Service SHALL 支持通过环境变量配置敏感信息（API 密钥、数据库连接字符串）
8.2 THE Configuration_Service SHALL 支持通过配置文件（YAML/JSON）配置业务参数
8.3 THE Configuration_Service SHALL 提供以下可配置项：抓取频率范围和默认值、校验阈值（质量分数、置信度）、健康度评估阈值、AI 服务参数（模型名称、temperature、max_tokens）、重试策略参数、重构触发阈值
8.4 WHEN 管理员修改配置 THEN Configuration_Service SHALL 验证配置值的有效性并拒绝无效配置
8.5 WHEN 配置变更 THEN Configuration_Service SHALL 记录变更历史（变更时间、变更者、变更前后值）
8.6 THE Configuration_Service SHALL 支持配置的热更新（无需重启服务即可生效）
8.7 THE Configuration_Service SHALL 提供配置查询和修改的 API 接口

### 需求 9：定时任务管理界面

**用户故事：** 作为管理员，我希望通过界面管理定时任务，以便监控任务执行状态和手动干预。

#### 验收标准

9.1 WHEN 管理员访问任务管理页面 THEN Task_Management_View SHALL 展示所有定时任务的列表，包含任务名称、执行频率、状态、上次执行时间、下次执行时间
9.2 WHEN 管理员点击任务 THEN Task_Management_View SHALL 展示最近 20 条执行记录，包含执行时间、耗时、结果
9.3 WHEN 管理员手动触发任务 THEN Task_Management_View SHALL 立即执行该任务并显示执行进度
9.4 WHEN 管理员暂停任务 THEN Task_Management_View SHALL 停止该任务的自动调度并显示暂停状态
9.5 THE Task_Management_View SHALL 显示任务执行成功率的统计图表

### 需求 10：系统配置界面

**用户故事：** 作为管理员，我希望通过界面管理系统配置，以便方便地调整系统参数。

#### 验收标准

10.1 WHEN 管理员访问配置页面 THEN Config_View SHALL 展示所有可配置项，按类别分组显示
10.2 WHEN 管理员修改配置 THEN Config_View SHALL 提供表单验证并显示配置说明
10.3 WHEN 配置保存成功 THEN Config_View SHALL 显示成功提示并立即生效
10.4 WHEN 管理员查看配置历史 THEN Config_View SHALL 展示配置变更记录列表
10.5 THE Config_View SHALL 对敏感配置项（API 密钥等）进行脱敏显示
