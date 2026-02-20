# 需求文档 - 迭代 3：用户输入与金字塔进化

## 概述

本文档描述 AI Radar 系统迭代 3 的需求。迭代 3 的核心目标是实现用户多模态输入、AI 驱动的概念提取、变更提案系统和人类审批机制，使系统能够通过用户贡献和 AI 分析持续进化知识金字塔结构。

## 迭代目标

1. 实现用户多模态内容输入（URL、PDF、Word、Markdown、图片、文本）
2. 构建 AI 概念提取与金字塔变更提案生成系统
3. 实现审批队列管理和决策执行机制
4. 构建变更影响分析和回滚机制
5. 实现用户贡献追踪系统
6. 构建审批中心界面

## 核心理念

- **AI 提议，人类决策**：所有结构性变更必须经过人类审批
- **透明可追溯**：每个 AI 建议都有清晰的推理过程和依据
- **安全可回滚**：所有变更都可以安全回滚到之前状态

## 依赖

- 迭代 1 完成的基础架构（金字塔、节点、信息源、内容数据模型）
- 迭代 2 完成的信息抓取系统（抓取引擎、校验机制、AI 服务集成）

## 术语表

- **Change_Proposal**：变更提案，AI 生成的对金字塔结构的修改建议
- **Approval_Queue**：审批队列，待人类审批的变更提案队列
- **State_Snapshot**：状态快照，变更前保存的系统状态
- **Contribution**：用户贡献，用户提交的内容记录
- **Concept**：概念，从内容中提取的关键知识点
- **Impact_Analysis**：影响分析，变更对系统的影响评估报告

## 需求

### 需求 1：用户多模态内容输入

**用户故事：** 作为用户，我希望能够通过多种方式提交内容，以便将各种格式的知识贡献到系统中。

#### 验收标准

1.1 WHEN 用户提交 URL 链接 THEN Input_Processor SHALL 调用抓取引擎获取页面内容并提取正文
1.2 WHEN 用户上传 PDF 文档 THEN Input_Processor SHALL 解析 PDF 并提取文本内容
1.3 WHEN 用户上传 Word 文档（.docx）THEN Input_Processor SHALL 解析文档并提取文本内容
1.4 WHEN 用户上传 Markdown 文件 THEN Input_Processor SHALL 解析 Markdown 并转换为纯文本
1.5 WHEN 用户上传图片文件 THEN Input_Processor SHALL 调用 OCR 服务提取图片中的文字
1.6 WHEN 用户提交纯文本 THEN Input_Processor SHALL 直接接收并处理文本内容
1.7 WHEN 用户批量提交多个输入 THEN Input_Processor SHALL 创建批量处理任务并逐个处理
1.8 IF 输入内容解析失败 THEN Input_Processor SHALL 返回详细错误信息并记录失败原因
1.9 THE Input_Processor SHALL 对每个成功处理的输入创建 Contribution 记录

### 需求 2：AI 概念提取

**用户故事：** 作为系统，我需要从用户提交的内容中自动识别关键概念，以便分析内容与知识金字塔的关系。

#### 验收标准

2.1 WHEN 内容完成预处理 THEN Concept_Extractor SHALL 调用 AI 服务识别内容中的关键概念
2.2 WHEN AI 返回概念列表 THEN Concept_Extractor SHALL 为每个概念提供名称、类型和置信度分数
2.3 WHEN 概念类型为"技术"THEN Concept_Extractor SHALL 标记为 technology 类型
2.4 WHEN 概念类型为"工具"THEN Concept_Extractor SHALL 标记为 tool 类型
2.5 WHEN 概念类型为"方法"THEN Concept_Extractor SHALL 标记为 method 类型
2.6 WHEN 概念类型为"组织"THEN Concept_Extractor SHALL 标记为 organization 类型
2.7 THE Concept_Extractor SHALL 返回概念之间的关联关系
2.8 THE Concept_Extractor SHALL 记录 AI 提取的完整推理过程

### 需求 3：概念与金字塔匹配

**用户故事：** 作为系统，我需要将提取的概念与现有金字塔节点进行匹配，以便确定是否需要结构变更。

#### 验收标准

3.1 WHEN 概念提取完成 THEN Concept_Matcher SHALL 搜索金字塔中是否存在相同或相似的节点
3.2 WHEN 找到完全匹配的节点 THEN Concept_Matcher SHALL 将内容关联到该节点
3.3 WHEN 找到相似节点（相似度 > 0.8）THEN Concept_Matcher SHALL 生成节点重命名或拆分的 Change_Proposal
3.4 WHEN 未找到匹配节点 THEN Concept_Matcher SHALL 生成添加新节点的 Change_Proposal
3.5 WHEN 发现概念间存在新关联 THEN Concept_Matcher SHALL 生成建立节点关联的 Change_Proposal
3.6 THE Concept_Matcher SHALL 维护同义词映射表，用于概念匹配
3.7 THE Concept_Matcher SHALL 记录匹配决策的依据和置信度

### 需求 4：变更提案生成

**用户故事：** 作为系统，我需要生成结构化的变更提案，以便人类审批者能够清晰理解变更内容。

#### 验收标准

4.1 WHEN 生成添加节点提案 THEN Proposal_Generator SHALL 包含新节点名称、描述、建议父节点、变更理由
4.2 WHEN 生成重命名节点提案 THEN Proposal_Generator SHALL 包含原名称、新名称、重命名理由
4.3 WHEN 生成拆分节点提案 THEN Proposal_Generator SHALL 包含原节点、拆分后的子节点列表、拆分理由
4.4 WHEN 生成合并节点提案 THEN Proposal_Generator SHALL 包含待合并节点列表、合并后名称、合并理由
4.5 WHEN 生成建立关联提案 THEN Proposal_Generator SHALL 包含源节点、目标节点、关联类型、关联理由
4.6 THE Proposal_Generator SHALL 为每个提案生成唯一标识符
4.7 THE Proposal_Generator SHALL 记录提案的来源内容和触发条件

### 需求 5：审批队列管理

**用户故事：** 作为管理员，我希望能够查看和管理所有待审批的变更提案，以便有序地处理系统变更。

#### 验收标准

5.1 WHEN 新提案生成 THEN Approval_Queue_Manager SHALL 将提案加入队列并分配唯一标识
5.2 WHEN 提案入队 THEN Approval_Queue_Manager SHALL 根据提案类型和影响范围计算优先级
5.3 WHEN 管理员查询队列 THEN Approval_Queue_Manager SHALL 返回按优先级和提交时间排序的提案列表
5.4 WHEN 管理员筛选提案 THEN Approval_Queue_Manager SHALL 支持按类型、状态、时间范围过滤
5.5 WHEN 提案在队列中超过 7 天 THEN Approval_Queue_Manager SHALL 发送超时提醒通知
5.6 WHEN 管理员查看提案详情 THEN Approval_Queue_Manager SHALL 返回完整提案信息、变更预览和影响分析
5.7 THE Approval_Queue_Manager SHALL 支持批量审批操作

### 需求 6：变更影响分析

**用户故事：** 作为管理员，我希望在审批前了解变更的影响范围，以便做出明智的决策。

#### 验收标准

6.1 WHEN 请求影响分析 THEN Impact_Analyzer SHALL 分析受影响的节点数量
6.2 WHEN 请求影响分析 THEN Impact_Analyzer SHALL 分析受影响的内容数量
6.3 WHEN 请求影响分析 THEN Impact_Analyzer SHALL 分析受影响的信息源映射
6.4 WHEN 请求影响分析 THEN Impact_Analyzer SHALL 评估变更风险等级（低/中/高）
6.5 WHEN 变更涉及删除或合并节点 THEN Impact_Analyzer SHALL 列出所有需要重新分类的内容
6.6 THE Impact_Analyzer SHALL 生成完整的影响分析报告
6.7 THE Impact_Analyzer SHALL 提供变更前后的对比预览

### 需求 7：审批决策执行

**用户故事：** 作为管理员，我希望能够批准、拒绝或修改变更提案，并确保决策被正确执行。

#### 验收标准

7.1 WHEN 管理员批准提案 THEN Decision_Executor SHALL 执行变更操作并更新金字塔结构
7.2 WHEN 变更执行成功 THEN Decision_Executor SHALL 更新提案状态为"已批准"并记录执行时间
7.3 IF 变更执行失败 THEN Decision_Executor SHALL 回滚所有已执行的操作并记录失败原因
7.4 WHEN 管理员拒绝提案 THEN Decision_Executor SHALL 更新提案状态为"已拒绝"并记录拒绝原因
7.5 WHEN 管理员修改提案 THEN Decision_Executor SHALL 创建新版本提案并保留原提案历史
7.6 THE Decision_Executor SHALL 支持变更预览模式（dry-run），不实际执行变更
7.7 THE Decision_Executor SHALL 记录所有审批决策的历史

### 需求 8：状态快照与回滚

**用户故事：** 作为管理员，我希望能够在变更出现问题时回滚到之前的状态，以便保证系统稳定性。

#### 验收标准

8.1 WHEN 变更执行前 THEN Snapshot_Manager SHALL 保存变更前的状态快照
8.2 WHEN 管理员请求回滚 THEN Snapshot_Manager SHALL 恢复到变更前的状态
8.3 WHEN 回滚完成 THEN Snapshot_Manager SHALL 记录回滚操作的详细信息
8.4 THE Snapshot_Manager SHALL 支持回滚到指定的历史版本
8.5 THE Snapshot_Manager SHALL 在回滚前提供状态预览
8.6 THE Snapshot_Manager SHALL 保留最近 30 天的状态快照
8.7 IF 快照数据损坏 THEN Snapshot_Manager SHALL 返回错误并阻止回滚操作

### 需求 9：用户贡献追踪

**用户故事：** 作为系统，我需要追踪用户的贡献记录，以便统计贡献情况和激励用户参与。

#### 验收标准

9.1 WHEN 用户提交内容 THEN Contribution_Tracker SHALL 记录提交者、提交时间、内容标识
9.2 WHEN 贡献内容被采纳 THEN Contribution_Tracker SHALL 更新贡献状态为"已采纳"
9.3 WHEN 贡献内容被拒绝 THEN Contribution_Tracker SHALL 更新贡献状态为"已拒绝"并记录原因
9.4 WHEN 用户查询贡献历史 THEN Contribution_Tracker SHALL 返回该用户的所有贡献记录
9.5 THE Contribution_Tracker SHALL 统计用户的贡献数量和采纳率
9.6 THE Contribution_Tracker SHALL 支持匿名贡献
9.7 THE Contribution_Tracker SHALL 记录贡献触发的变更提案关联

### 需求 10：审批中心界面

**用户故事：** 作为管理员，我希望通过直观的界面管理所有审批事项，以便高效处理变更提案。

#### 验收标准

10.1 WHEN 管理员访问审批中心 THEN Approval_Center_View SHALL 展示待审批提案队列
10.2 WHEN 展示提案列表 THEN Approval_Center_View SHALL 显示提案类型、标题、提交时间、优先级
10.3 WHEN 管理员点击提案 THEN Approval_Center_View SHALL 展示提案详情、变更预览和影响分析
10.4 WHEN 管理员操作提案 THEN Approval_Center_View SHALL 提供批准、拒绝、修改操作按钮
10.5 WHEN 管理员查看历史 THEN Approval_Center_View SHALL 展示已处理提案的历史记录
10.6 THE Approval_Center_View SHALL 在导航栏显示待审批数量徽章
10.7 THE Approval_Center_View SHALL 支持批量选择和批量操作

### 需求 11：内容输入界面

**用户故事：** 作为用户，我希望通过简洁的界面提交各种格式的内容，以便方便地贡献知识。

#### 验收标准

11.1 WHEN 用户访问输入页面 THEN Input_View SHALL 展示多种输入方式选项
11.2 WHEN 用户选择 URL 输入 THEN Input_View SHALL 展示 URL 输入框和提交按钮
11.3 WHEN 用户选择文件上传 THEN Input_View SHALL 展示文件拖拽区域，支持 PDF、Word、Markdown、图片
11.4 WHEN 用户选择文本输入 THEN Input_View SHALL 展示多行文本输入框
11.5 WHEN 内容处理中 THEN Input_View SHALL 显示处理进度和状态
11.6 WHEN 内容处理完成 THEN Input_View SHALL 显示提取的概念和生成的提案预览
11.7 THE Input_View SHALL 支持批量文件上传

### 需求 12：变更历史界面

**用户故事：** 作为管理员，我希望查看系统的变更历史，以便追溯和审计系统演变过程。

#### 验收标准

12.1 WHEN 管理员访问变更历史 THEN History_View SHALL 展示所有已执行变更的时间线
12.2 WHEN 展示变更记录 THEN History_View SHALL 显示变更类型、执行时间、执行者、影响范围
12.3 WHEN 管理员点击变更记录 THEN History_View SHALL 展示变更详情和执行前后对比
12.4 WHEN 管理员选择回滚 THEN History_View SHALL 展示回滚确认对话框和影响预览
12.5 THE History_View SHALL 支持按时间范围、变更类型筛选
12.6 THE History_View SHALL 支持导出变更历史报告

### 需求 13：提案优先级计算

**用户故事：** 作为系统，我需要自动计算提案优先级，以便管理员能够优先处理重要变更。

#### 验收标准

13.1 WHEN 计算优先级 THEN Priority_Calculator SHALL 考虑提案类型权重（删除 > 合并 > 拆分 > 添加 > 重命名）
13.2 WHEN 计算优先级 THEN Priority_Calculator SHALL 考虑影响范围（受影响节点和内容数量）
13.3 WHEN 计算优先级 THEN Priority_Calculator SHALL 考虑提案来源（用户贡献 vs 系统发现）
13.4 WHEN 计算优先级 THEN Priority_Calculator SHALL 考虑等待时间（越久优先级越高）
13.5 THE Priority_Calculator SHALL 返回 1-100 的优先级分数
13.6 THE Priority_Calculator SHALL 支持手动调整优先级

### 需求 14：同义词映射管理

**用户故事：** 作为管理员，我希望管理概念的同义词映射，以便提高概念匹配的准确性。

#### 验收标准

14.1 WHEN 管理员添加同义词 THEN Synonym_Manager SHALL 创建概念与同义词的映射关系
14.2 WHEN 管理员删除同义词 THEN Synonym_Manager SHALL 移除指定的映射关系
14.3 WHEN 概念匹配时 THEN Synonym_Manager SHALL 自动扩展搜索同义词
14.4 THE Synonym_Manager SHALL 支持批量导入同义词映射
14.5 THE Synonym_Manager SHALL 记录同义词映射的来源（手动/AI 建议）
14.6 THE Synonym_Manager SHALL 提供同义词管理界面

### 需求 15：AI 服务扩展

**用户故事：** 作为系统，我需要扩展 AI 服务能力，以支持概念提取和内容分析功能。

#### 验收标准

15.1 THE AI_Service SHALL 支持概念提取 API 调用
15.2 THE AI_Service SHALL 支持概念相似度计算 API 调用
15.3 THE AI_Service SHALL 支持变更理由生成 API 调用
15.4 THE AI_Service SHALL 支持 OCR 文字识别 API 调用
15.5 WHEN AI 服务调用失败 THEN AI_Service SHALL 实现指数退避重试
15.6 THE AI_Service SHALL 记录所有 AI 调用的输入输出和耗时
15.7 THE AI_Service SHALL 支持配置不同的 AI 模型

### 需求 16：文件解析服务

**用户故事：** 作为系统，我需要解析各种文件格式，以便提取用户上传文件的内容。

#### 验收标准

16.1 THE File_Parser SHALL 支持 PDF 文件解析，提取文本和元数据
16.2 THE File_Parser SHALL 支持 Word 文档（.docx）解析，提取文本和格式信息
16.3 THE File_Parser SHALL 支持 Markdown 文件解析，转换为纯文本
16.4 THE File_Parser SHALL 支持常见图片格式（PNG、JPG、JPEG）的 OCR 处理
16.5 IF 文件格式不支持 THEN File_Parser SHALL 返回明确的错误信息
16.6 IF 文件大小超过限制（默认 10MB）THEN File_Parser SHALL 拒绝处理并返回错误
16.7 THE File_Parser SHALL 记录文件解析的耗时和结果

### 需求 17：批量处理任务

**用户故事：** 作为用户，我希望能够批量提交内容，以便高效地贡献大量知识。

#### 验收标准

17.1 WHEN 用户提交批量任务 THEN Batch_Processor SHALL 创建批量任务记录并返回任务 ID
17.2 WHEN 批量任务执行 THEN Batch_Processor SHALL 逐个处理输入项并记录进度
17.3 WHEN 单个输入处理失败 THEN Batch_Processor SHALL 记录错误并继续处理其他输入
17.4 WHEN 用户查询任务状态 THEN Batch_Processor SHALL 返回任务进度和各项处理结果
17.5 THE Batch_Processor SHALL 支持取消正在执行的批量任务
17.6 THE Batch_Processor SHALL 限制单次批量任务的最大输入数量（默认 50）

### 需求 18：通知服务

**用户故事：** 作为管理员，我希望收到重要事件的通知，以便及时处理审批事项。

#### 验收标准

18.1 WHEN 新提案生成 THEN Notification_Service SHALL 发送新提案通知
18.2 WHEN 提案超时 THEN Notification_Service SHALL 发送超时提醒通知
18.3 WHEN 高优先级提案入队 THEN Notification_Service SHALL 发送紧急通知
18.4 THE Notification_Service SHALL 支持站内通知
18.5 THE Notification_Service SHALL 记录通知发送历史
18.6 THE Notification_Service SHALL 支持配置通知偏好

