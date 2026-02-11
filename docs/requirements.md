# 需求文档

## 简介

AI Radar 是一个面向大模型应用领域的自进化知识聚合平台。该系统具备感知、认知、进化能力，通过 AI 驱动持续自我完善，人类作为最终决策者把控方向。

## 核心哲学

### 第一性原理：自进化系统

AI Radar 的核心定位是一个**会自我进化的知识系统**，而非静态的信息聚合网站。这意味着：

1. **系统即生命体**：系统具备感知（信息抓取）、认知（内容理解）、进化（结构优化）三大能力
2. **知识即有机体**：知识结构不是固定的分类目录，而是随领域发展动态生长的有机体
3. **进化即常态**：变化是系统的正常状态，稳定只是暂时的平衡

### 三大核心理念

#### 理念一：一切皆可进化
- **金字塔结构可进化**：节点可增删、层级可调整、关系可重构
- **信息源可进化**：来源可发现、可淘汰、可自适应调整
- **抓取策略可进化**：频率、深度、规则都根据效果动态调整
- **系统自身可进化**：通过反馈循环持续优化各个模块

#### 理念二：AI 提议，人类决策
- **AI 是顾问**：AI 负责发现问题、分析数据、生成建议
- **人类是决策者**：所有结构性变更必须经过人类审批
- **透明可追溯**：每个 AI 建议都有清晰的推理过程和依据
- **渐进式信任**：随着 AI 建议准确率提升，可逐步扩大自动化范围

#### 理念三：信息可靠性优先
- **只采信权威一手源**：优先官方发布、学术论文、权威媒体
- **三层校验机制**：硬性规则校验 + AI 质量评估 + 多源交叉验证
- **透明展示校验过程**：用户可查看每条信息的完整校验链路
- **宁缺毋滥**：宁可漏掉信息，不可传播不实内容

### 系统能力模型

```
┌─────────────────────────────────────────────────────────────┐
│                      人类决策层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  审批决策   │  │  方向把控   │  │  规则制定   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      AI 认知层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  内容理解   │  │  模式识别   │  │  建议生成   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      感知执行层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  信息抓取   │  │  内容校验   │  │  状态监测   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      知识组织层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  金字塔结构  │  │  信息源网络  │  │  内容存储   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 进化循环模型

系统通过以下循环实现持续进化：

```
感知 → 理解 → 评估 → 建议 → 审批 → 执行 → 反馈 → 感知
  │       │       │       │       │       │       │
  │       │       │       │       │       │       └── 效果数据
  │       │       │       │       │       └── 变更实施
  │       │       │       │       └── 人类决策
  │       │       │       └── AI 生成提案
  │       │       └── 健康度检测
  │       └── AI 内容分析
  └── 信息抓取
```

### 信息可信度模型

每条信息的可信度由以下因素综合决定：

```
可信度 = f(来源权威性, 校验通过率, 多源确认度, 时效性)

其中：
- 来源权威性：官方 > 学术 > 权威媒体 > 社区 > 个人
- 校验通过率：硬性校验 × 软性校验 × 交叉验证
- 多源确认度：独立信息源确认数量
- 时效性：信息发布时间与当前时间的关系
```

## 系统边界

### 功能边界
- 本系统专注于 AI 应用领域的知识聚合
- 不涉及用户社交、评论互动等社区功能（首期）
- 不涉及付费订阅、商业变现等商业功能（首期）

### 技术边界
- 前端：Next.js + Tailwind CSS + ReactFlow
- 后端：Python FastAPI
- AI 服务：硅基流动 API
- 数据库：PostgreSQL（生产）或 SQLite（开发）
- 部署：本地开发环境，后续支持 Docker 部署

### 迭代边界
- 迭代 1：骨架搭建（基础架构、核心数据模型、基本 UI）
- 迭代 2：信息抓取（动态信息源、抓取引擎、校验机制）
- 迭代 3：用户输入与金字塔进化（多模态输入、概念提取、审批系统）
- 迭代 4：自我进化（健康检测、重构建议、策略自适应）
- 迭代 5：完善与 Docker 化（性能优化、监控完善、容器部署）

## 术语表

- **Knowledge_Pyramid（知识金字塔）**: 层级化的知识组织结构，每个金字塔代表一个知识领域（如 AI 开发工具链、Agent 生态、Prompt 工程等）
- **Pyramid_Node（金字塔节点）**: 金字塔中的单个知识单元，具有父子层级关系，可关联多个信息源和内容
- **Pyramid_Health（金字塔健康度）**: 衡量金字塔结构合理性的指标，包括深度平衡性、节点覆盖度、更新活跃度
- **Information_Source（信息源）**: 提供内容的数据来源，支持 RSS、API、网页爬取、用户贡献四种类型
- **Source_Lifecycle（信息源生命周期）**: 信息源的状态流转：发现→验证→活跃→监测→调整→淘汰
- **Source_Health（信息源健康度）**: 衡量信息源质量的指标，包括可达性、更新频率、内容质量、响应时间
- **Content_Item（内容条目）**: 从信息源抓取或用户提交的单条信息，包含原文、摘要、校验状态、分类等
- **Hard_Validation（硬性校验）**: 基于规则的校验，包括 URL 可达性、域名白名单、论文 ID 格式等
- **Soft_Validation（软性校验）**: 基于 AI 的校验，评估内容质量、与声明一致性、可信度等
- **Cross_Validation（交叉验证）**: 多源确认机制，检查是否有多个独立信息源报道相同信息
- **Validation_Result（校验结果）**: 包含三层校验的详细结果、通过状态、失败原因
- **Approval_Queue（审批队列）**: 存储待人类审批的变更提案，按优先级和时间排序
- **Change_Proposal（变更提案）**: AI 生成的变更建议，包含变更类型、目标对象、变更内容、理由
- **Proposal_Type（提案类型）**: 变更提案的分类：金字塔结构变更、信息源变更、策略变更
- **Health_Score（健康度评分）**: 0-100 的数值评分，用于量化各类健康指标
- **Hotspot（热点话题）**: 当前关注度高的话题，具有生命周期状态
- **Hotspot_Lifecycle（热点生命周期）**: 热点的状态流转：新兴→热门→成熟→冷却→归档
- **Concept_Drift（概念漂移）**: 术语或概念含义随时间发生的变化
- **Crawl_Strategy（抓取策略）**: 定义抓取行为的配置，包括频率、深度、选择器、重试策略
- **Crawl_Job（抓取任务）**: 单次抓取执行的记录，包含状态、结果、耗时等
- **Evolution_Engine（进化引擎）**: 负责系统自我优化的核心模块
- **AI_Summary（AI 摘要）**: AI 生成的内容摘要，包含关键信息提取
- **Concept_Entity（概念实体）**: 从内容中提取的关键概念，包含名称、类型、置信度
- **User_Contribution（用户贡献）**: 用户提交的内容，需要经过校验流程
- **Feed_Item（信息流条目）**: 展示给用户的内容单元，包含标题、摘要、来源、时间等
- **Domain_Whitelist（域名白名单）**: 可信域名列表，用于硬性校验
- **Paper_ID_Pattern（论文 ID 模式）**: 用于验证学术论文 ID 格式的正则表达式

## 需求

### 需求 1：知识金字塔核心管理

**用户故事：** 作为知识管理员，我希望能够创建和管理多个独立但可关联的知识金字塔，以便系统化地组织 AI 应用领域的知识。

#### 验收标准

1. WHEN 管理员创建新金字塔 THEN Knowledge_Pyramid_Manager SHALL 创建包含唯一标识、名称、描述、创建时间、根节点的金字塔实例
2. WHEN 管理员编辑金字塔基本信息 THEN Knowledge_Pyramid_Manager SHALL 更新金字塔的名称和描述
3. WHEN 管理员删除金字塔 THEN Knowledge_Pyramid_Manager SHALL 移除金字塔及其所有节点、关联的信息源映射，并归档相关内容
4. WHEN 管理员查询金字塔列表 THEN Knowledge_Pyramid_Manager SHALL 返回所有金字塔的基本信息和健康度摘要
5. WHEN 管理员查询单个金字塔详情 THEN Knowledge_Pyramid_Manager SHALL 返回金字塔完整结构、统计信息和健康度详情
6. THE Knowledge_Pyramid_Manager SHALL 支持预设的金字塔模板（AI 开发工具链、Agent 生态、Prompt 工程、模型应用能力、热点追踪）

### 需求 2：金字塔节点管理

**用户故事：** 作为知识管理员，我希望能够灵活管理金字塔中的节点，以便精细化组织知识结构。

#### 验收标准

1. WHEN 管理员添加节点 THEN Pyramid_Node_Manager SHALL 在指定父节点下创建包含唯一标识、名称、描述、层级、排序权重的新节点
2. WHEN 管理员编辑节点 THEN Pyramid_Node_Manager SHALL 更新节点的名称、描述和排序权重
3. WHEN 管理员删除节点 THEN Pyramid_Node_Manager SHALL 移除该节点及其所有子节点，并将关联内容标记为待重新分类
4. WHEN 管理员移动节点 THEN Pyramid_Node_Manager SHALL 将节点移动到新的父节点下，保持其子节点关系不变
5. WHEN 管理员拆分节点 THEN Pyramid_Node_Manager SHALL 将单个节点拆分为指定数量的子节点，并根据 AI 建议重新分配关联内容
6. WHEN 管理员合并节点 THEN Pyramid_Node_Manager SHALL 将多个同级节点合并为一个，整合所有关联内容和信息源映射
7. WHEN 管理员设置节点关联 THEN Pyramid_Node_Manager SHALL 建立跨金字塔的节点关联关系
8. WHEN 查询节点详情 THEN Pyramid_Node_Manager SHALL 返回节点信息、子节点列表、关联内容数量、关联信息源列表

### 需求 3：金字塔可视化与健康度

**用户故事：** 作为用户，我希望能够直观地查看金字塔结构和健康状态，以便快速了解知识组织情况。

#### 验收标准

1. WHEN 用户请求金字塔可视化数据 THEN Visualization_Service SHALL 返回包含节点位置、层级、连接关系的可渲染数据结构
2. WHEN 用户请求特定节点的子树 THEN Visualization_Service SHALL 返回以该节点为根的子树可视化数据
3. WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估深度平衡性（各分支深度差异）并返回 0-100 的评分
4. WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估节点覆盖度（是否有空节点或过载节点）并返回 0-100 的评分
5. WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估更新活跃度（近期内容更新频率）并返回 0-100 的评分
6. WHEN 健康度低于阈值 THEN Health_Evaluator SHALL 生成具体的问题描述和改进建议
7. THE Visualization_Service SHALL 支持按健康度、内容数量、更新时间对节点进行颜色编码

### 需求 4：信息源基础管理

**用户故事：** 作为系统管理员，我希望能够添加和配置各类信息源，以便从多渠道获取 AI 领域信息。

#### 验收标准

1. WHEN 管理员添加 RSS 信息源 THEN Information_Source_Manager SHALL 创建包含 URL、名称、更新检查频率、关联节点列表的信息源记录
2. WHEN 管理员添加 API 信息源 THEN Information_Source_Manager SHALL 创建包含端点 URL、认证方式、请求头、请求参数、响应解析规则的信息源记录
3. WHEN 管理员添加网页爬取信息源 THEN Information_Source_Manager SHALL 创建包含目标 URL、CSS/XPath 选择器、分页规则、抓取深度的信息源记录
4. WHEN 管理员编辑信息源 THEN Information_Source_Manager SHALL 更新信息源的配置参数
5. WHEN 管理员删除信息源 THEN Information_Source_Manager SHALL 移除信息源记录，保留已抓取的内容但标记来源已删除
6. WHEN 管理员查询信息源列表 THEN Information_Source_Manager SHALL 返回所有信息源的基本信息、状态、健康度
7. WHEN 管理员测试信息源 THEN Information_Source_Manager SHALL 执行一次测试抓取并返回结果预览
8. THE Information_Source_Manager SHALL 为每个信息源类型提供配置模板和示例

### 需求 5：信息源生命周期管理

**用户故事：** 作为系统管理员，我希望系统能够自动管理信息源的生命周期，以便维护信息源的质量和有效性。

#### 验收标准

1. WHEN 新信息源被添加 THEN Source_Lifecycle_Manager SHALL 将其状态设置为"发现"并安排验证任务
2. WHEN 信息源通过初始验证 THEN Source_Lifecycle_Manager SHALL 将状态更新为"验证"并开始试运行抓取
3. WHEN 信息源试运行成功 THEN Source_Lifecycle_Manager SHALL 将状态更新为"活跃"并纳入正常抓取调度
4. WHEN 活跃信息源出现异常 THEN Source_Lifecycle_Manager SHALL 将状态更新为"监测"并增加检查频率
5. WHEN 监测期信息源恢复正常 THEN Source_Lifecycle_Manager SHALL 将状态恢复为"活跃"
6. WHEN 监测期信息源持续异常 THEN Source_Lifecycle_Manager SHALL 将状态更新为"调整"并生成调整建议的 Change_Proposal
7. WHEN 信息源被判定为无效 THEN Source_Lifecycle_Manager SHALL 将状态更新为"淘汰"并停止抓取
8. THE Source_Lifecycle_Manager SHALL 记录每次状态变更的时间、原因和操作者

### 需求 6：信息源健康监测

**用户故事：** 作为系统管理员，我希望能够实时了解信息源的健康状态，以便及时发现和处理问题。

#### 验收标准

1. WHEN 系统执行健康检查 THEN Health_Monitor SHALL 检测信息源的可达性并记录响应时间
2. WHEN 系统执行健康检查 THEN Health_Monitor SHALL 统计信息源的更新频率是否符合预期
3. WHEN 系统执行健康检查 THEN Health_Monitor SHALL 评估最近抓取内容的质量分数均值
4. WHEN 系统执行健康检查 THEN Health_Monitor SHALL 计算抓取成功率（成功次数/总次数）
5. WHEN 健康指标异常 THEN Health_Monitor SHALL 生成告警并更新信息源状态
6. WHEN 管理员查看健康报告 THEN Health_Monitor SHALL 返回各信息源的健康指标趋势图数据
7. THE Health_Monitor SHALL 每小时执行一次常规健康检查
8. THE Health_Monitor SHALL 支持手动触发即时健康检查

### 需求 7：信息源自动发现

**用户故事：** 作为系统，我希望能够自动发现新的潜在信息源，以便持续扩展知识获取渠道。

#### 验收标准

1. WHEN 内容中包含外部链接 THEN Source_Discovery_Service SHALL 提取并分析链接指向的域名
2. WHEN 发现新域名频繁出现 THEN Source_Discovery_Service SHALL 评估该域名作为信息源的潜力
3. WHEN 域名评估通过 THEN Source_Discovery_Service SHALL 生成新信息源的 Change_Proposal
4. WHEN 用户提交的内容包含信息源线索 THEN Source_Discovery_Service SHALL 提取并评估潜在信息源
5. THE Source_Discovery_Service SHALL 维护已评估域名的记录，避免重复评估
6. THE Source_Discovery_Service SHALL 优先发现与现有金字塔节点相关的信息源

### 需求 8：内容抓取引擎

**用户故事：** 作为系统，我需要定时从各信息源抓取内容，以便保持知识库的更新。

#### 验收标准

1. WHEN 定时任务触发 THEN Crawl_Engine SHALL 根据各信息源的配置频率创建抓取任务
2. WHEN 执行 RSS 抓取 THEN Crawl_Engine SHALL 解析 RSS/Atom 格式并提取条目列表
3. WHEN 执行 API 抓取 THEN Crawl_Engine SHALL 按配置发送请求并解析响应数据
4. WHEN 执行网页抓取 THEN Crawl_Engine SHALL 使用配置的选择器提取目标内容
5. WHEN 抓取完成 THEN Crawl_Engine SHALL 对新内容进行去重检查
6. WHEN 发现新内容 THEN Crawl_Engine SHALL 创建 Content_Item 并提交到校验流程
7. IF 抓取失败 THEN Crawl_Engine SHALL 记录错误信息并按重试策略安排重试
8. THE Crawl_Engine SHALL 记录每次抓取任务的开始时间、结束时间、抓取数量、成功率
9. THE Crawl_Engine SHALL 支持并发抓取，但对同一域名限制请求频率
10. THE Crawl_Engine SHALL 遵守 robots.txt 规则

### 需求 9：内容硬性校验

**用户故事：** 作为系统，我需要对抓取的内容进行基础规则校验，以便过滤明显无效的内容。

#### 验收标准

1. WHEN 内容进入硬性校验 THEN Hard_Validator SHALL 验证内容 URL 的可达性
2. WHEN 内容进入硬性校验 THEN Hard_Validator SHALL 检查内容来源域名是否在白名单中
3. WHEN 内容包含论文引用 THEN Hard_Validator SHALL 验证论文 ID 格式（arXiv、DOI 等）的正确性
4. WHEN 内容包含代码仓库链接 THEN Hard_Validator SHALL 验证仓库链接的有效性
5. WHEN 内容包含日期信息 THEN Hard_Validator SHALL 验证日期格式和合理性
6. IF 硬性校验失败 THEN Hard_Validator SHALL 返回失败原因列表
7. THE Hard_Validator SHALL 支持配置自定义校验规则
8. THE Hard_Validator SHALL 记录每条校验规则的执行结果

### 需求 10：内容软性校验

**用户故事：** 作为系统，我需要使用 AI 评估内容质量，以便筛选高质量信息。

#### 验收标准

1. WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用 AI 服务评估内容的信息密度（0-100 分）
2. WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用 AI 服务评估内容的原创性（0-100 分）
3. WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用 AI 服务评估内容与标题的一致性（0-100 分）
4. WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用 AI 服务检测是否为广告或营销内容
5. WHEN 内容进入软性校验 THEN Soft_Validator SHALL 调用 AI 服务评估内容的时效性
6. WHEN 软性校验完成 THEN Soft_Validator SHALL 计算综合质量分数
7. IF 综合质量分数低于阈值 THEN Soft_Validator SHALL 标记内容为低质量并记录原因
8. THE Soft_Validator SHALL 返回详细的评估报告，包含各维度分数和 AI 评语

### 需求 11：内容交叉验证

**用户故事：** 作为系统，我需要通过多源确认来验证信息的可靠性，以便提高内容可信度。

#### 验收标准

1. WHEN 内容进入交叉验证 THEN Cross_Validator SHALL 搜索是否有其他信息源报道相同主题
2. WHEN 找到相关内容 THEN Cross_Validator SHALL 调用 AI 服务比较内容的一致性
3. WHEN 多个独立源确认相同信息 THEN Cross_Validator SHALL 提升内容的可信度评分
4. WHEN 发现信息冲突 THEN Cross_Validator SHALL 标记冲突并记录各源的说法
5. IF 无法找到其他源确认 THEN Cross_Validator SHALL 标记为"单源信息"并降低可信度权重
6. THE Cross_Validator SHALL 记录交叉验证的详细过程和结果
7. THE Cross_Validator SHALL 在内容展示时显示验证状态（多源确认/单源/存在冲突）

### 需求 12：内容处理与分类

**用户故事：** 作为系统，我需要对通过校验的内容进行处理和分类，以便将其纳入知识体系。

#### 验收标准

1. WHEN 内容通过所有校验 THEN AI_Summary_Service SHALL 生成 100-200 字的内容摘要
2. WHEN 内容通过所有校验 THEN AI_Summary_Service SHALL 提取 3-5 个关键标签
3. WHEN 内容完成摘要生成 THEN Content_Classifier SHALL 调用 AI 服务推荐最相关的金字塔节点
4. WHEN AI 推荐节点置信度高于阈值 THEN Content_Classifier SHALL 自动将内容分类到该节点
5. WHEN AI 推荐节点置信度低于阈值 THEN Content_Classifier SHALL 将内容加入人工分类队列
6. WHEN 内容可能属于多个节点 THEN Content_Classifier SHALL 支持多节点关联
7. THE Content_Classifier SHALL 记录分类决策的依据和置信度
8. THE Content_Classifier SHALL 支持人工调整分类结果

### 需求 13：用户多模态输入

**用户故事：** 作为普通用户，我希望能够通过多种方式提交信息，以便方便地贡献内容。

#### 验收标准

1. WHEN 用户提交 URL 链接 THEN Input_Processor SHALL 抓取链接内容并提取标题、正文、发布时间
2. WHEN 用户上传 PDF 文档 THEN Input_Processor SHALL 解析 PDF 并提取文本内容
3. WHEN 用户上传 Word 文档 THEN Input_Processor SHALL 解析文档并提取文本内容
4. WHEN 用户上传 Markdown 文件 THEN Input_Processor SHALL 解析 Markdown 并提取结构化内容
5. WHEN 用户上传图片 THEN Input_Processor SHALL 调用 OCR 服务提取图片中的文字
6. WHEN 用户提交纯文本 THEN Input_Processor SHALL 直接处理文本内容
7. WHEN 输入处理完成 THEN Input_Processor SHALL 创建 User_Contribution 记录并提交到校验流程
8. THE Input_Processor SHALL 支持批量输入处理
9. THE Input_Processor SHALL 返回处理状态和预览结果

### 需求 14：概念提取与金字塔变更提案

**用户故事：** 作为系统，我需要从用户输入中提取概念并生成金字塔变更建议，以便推动知识结构的进化。

#### 验收标准

1. WHEN 输入内容完成解析 THEN Concept_Extractor SHALL 调用 AI 服务识别内容中的关键概念
2. WHEN 概念提取完成 THEN Concept_Extractor SHALL 返回概念列表，每个概念包含名称、类型、置信度
3. WHEN 提取的概念在现有金字塔中不存在 THEN Proposal_Generator SHALL 生成添加新节点的 Change_Proposal
4. WHEN 提取的概念与现有节点相似但不完全匹配 THEN Proposal_Generator SHALL 生成节点重命名或拆分的 Change_Proposal
5. WHEN 发现概念间的新关联关系 THEN Proposal_Generator SHALL 生成建立节点关联的 Change_Proposal
6. THE Concept_Extractor SHALL 维护已知概念的同义词映射
7. THE Proposal_Generator SHALL 在提案中包含变更理由和影响分析

### 需求 15：审批队列管理

**用户故事：** 作为系统管理员，我希望能够高效管理审批队列，以便及时处理变更提案。

#### 验收标准

1. WHEN 系统生成 Change_Proposal THEN Approval_Queue_Manager SHALL 将提案加入队列并分配唯一标识
2. WHEN 提案加入队列 THEN Approval_Queue_Manager SHALL 根据提案类型和影响范围计算优先级
3. WHEN 管理员查看队列 THEN Approval_Queue_Manager SHALL 返回按优先级和提交时间排序的提案列表
4. WHEN 管理员筛选队列 THEN Approval_Queue_Manager SHALL 支持按提案类型、状态、时间范围过滤
5. WHEN 提案在队列中超过指定时间 THEN Approval_Queue_Manager SHALL 发送提醒通知
6. THE Approval_Queue_Manager SHALL 显示每个提案的详细信息、变更预览和影响分析
7. THE Approval_Queue_Manager SHALL 支持批量审批操作

### 需求 16：审批决策执行

**用户故事：** 作为系统管理员，我希望能够对提案做出决策并看到执行结果，以便控制系统的进化方向。

#### 验收标准

1. WHEN 管理员批准提案 THEN Approval_Executor SHALL 执行提案中定义的变更操作
2. WHEN 变更执行成功 THEN Approval_Executor SHALL 更新提案状态为"已执行"并记录执行时间
3. IF 变更执行失败 THEN Approval_Executor SHALL 回滚已执行的部分操作并记录失败原因
4. WHEN 管理员拒绝提案 THEN Approval_Queue_Manager SHALL 更新提案状态为"已拒绝"
5. WHEN 管理员拒绝提案 THEN Approval_Queue_Manager SHALL 要求输入拒绝原因
6. WHEN 管理员修改提案 THEN Approval_Queue_Manager SHALL 创建提案的新版本并保留原版本记录
7. THE Approval_Executor SHALL 支持变更的预览模式（dry-run）
8. THE Change_History_Service SHALL 记录所有审批决策、执行结果和变更详情

### 需求 17：系统健康检测

**用户故事：** 作为系统，我需要持续监测自身健康状态，以便发现需要优化的问题。

#### 验收标准

1. WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估每个金字塔的结构平衡性
2. WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估所有信息源的整体健康状况
3. WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估热点话题的生命周期分布
4. WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估内容更新频率和覆盖度
5. WHEN 系统执行健康检测 THEN Health_Detector SHALL 评估审批队列的积压情况
6. WHEN 检测到健康问题 THEN Health_Detector SHALL 生成问题报告并触发相应的优化流程
7. THE Health_Detector SHALL 每天执行一次全面健康检测
8. THE Health_Detector SHALL 支持手动触发即时检测

### 需求 18：金字塔重构建议

**用户故事：** 作为系统，我需要能够识别金字塔结构问题并生成重构建议，以便优化知识组织。

#### 验收标准

1. WHEN 检测到节点内容过多 THEN Restructure_Advisor SHALL 生成节点拆分的 Change_Proposal
2. WHEN 检测到节点长期无内容 THEN Restructure_Advisor SHALL 生成节点删除或合并的 Change_Proposal
3. WHEN 检测到层级过深 THEN Restructure_Advisor SHALL 生成层级扁平化的 Change_Proposal
4. WHEN 检测到同级节点过多 THEN Restructure_Advisor SHALL 生成节点分组的 Change_Proposal
5. WHEN 检测到节点命名不一致 THEN Restructure_Advisor SHALL 生成重命名的 Change_Proposal
6. THE Restructure_Advisor SHALL 在提案中包含重构理由、预期效果和风险评估
7. THE Restructure_Advisor SHALL 支持配置重构触发阈值

### 需求 19：热点生命周期管理

**用户故事：** 作为系统，我需要追踪热点话题的生命周期，以便合理调整内容展示优先级。

#### 验收标准

1. WHEN 新话题出现频率超过阈值 THEN Hotspot_Lifecycle_Manager SHALL 将其标记为"新兴"热点
2. WHEN 新兴热点持续增长 THEN Hotspot_Lifecycle_Manager SHALL 将状态更新为"热门"
3. WHEN 热门话题增长放缓 THEN Hotspot_Lifecycle_Manager SHALL 将状态更新为"成熟"
4. WHEN 成熟话题关注度下降 THEN Hotspot_Lifecycle_Manager SHALL 将状态更新为"冷却"
5. WHEN 冷却话题长期无更新 THEN Hotspot_Lifecycle_Manager SHALL 将状态更新为"归档"
6. WHEN 热点状态变化 THEN Hotspot_Lifecycle_Manager SHALL 调整相关内容的展示优先级
7. THE Hotspot_Lifecycle_Manager SHALL 记录热点的完整生命周期轨迹
8. THE Hotspot_Lifecycle_Manager SHALL 支持手动调整热点状态

### 需求 20：概念漂移检测

**用户故事：** 作为系统，我需要检测术语含义的变化，以便保持知识库的准确性。

#### 验收标准

1. WHEN 系统分析内容 THEN Concept_Drift_Detector SHALL 监测关键术语的使用上下文
2. WHEN 术语使用上下文发生显著变化 THEN Concept_Drift_Detector SHALL 标记为潜在概念漂移
3. WHEN 检测到概念漂移 THEN Concept_Drift_Detector SHALL 生成术语定义更新的 Change_Proposal
4. WHEN 检测到概念漂移 THEN Concept_Drift_Detector SHALL 建议更新相关金字塔节点的描述
5. THE Concept_Drift_Detector SHALL 维护术语的历史定义版本
6. THE Concept_Drift_Detector SHALL 在检测报告中包含漂移证据和建议更新内容

### 需求 21：抓取策略自适应

**用户故事：** 作为系统，我需要根据抓取效果自动调整策略，以便优化信息获取效率。

#### 验收标准

1. WHEN 信息源更新频率变化 THEN Strategy_Optimizer SHALL 调整该源的抓取频率
2. WHEN 信息源响应时间变化 THEN Strategy_Optimizer SHALL 调整请求超时和重试参数
3. WHEN 抓取成功率下降 THEN Strategy_Optimizer SHALL 分析原因并调整抓取策略
4. WHEN 内容质量分数持续偏低 THEN Strategy_Optimizer SHALL 调整内容过滤规则
5. THE Strategy_Optimizer SHALL 记录每次策略调整的原因和效果
6. THE Strategy_Optimizer SHALL 支持配置策略调整的边界范围
7. THE Strategy_Optimizer SHALL 在重大策略变更时生成 Change_Proposal 供人工审批

### 需求 22：信息流浏览界面

**用户故事：** 作为终端用户，我希望能够方便地浏览最新信息，以便快速获取 AI 领域动态。

#### 验收标准

1. WHEN 用户访问信息流页面 THEN Feed_View SHALL 展示按时间倒序排列的内容列表
2. WHEN 用户选择快速浏览模式 THEN Feed_View SHALL 展示标题、摘要、来源、时间的紧凑视图
3. WHEN 用户选择深度阅读模式 THEN Feed_View SHALL 展示完整摘要、标签、校验状态、相关内容
4. WHEN 用户点击内容条目 THEN Feed_View SHALL 展示内容详情页，包含原文链接和完整校验报告
5. WHEN 用户筛选内容 THEN Feed_View SHALL 支持按金字塔节点、时间范围、质量分数、来源类型过滤
6. WHEN 用户搜索内容 THEN Feed_View SHALL 支持关键词全文搜索
7. THE Feed_View SHALL 支持无限滚动加载
8. THE Feed_View SHALL 显示内容的验证状态标识（多源确认/单源/待验证）

### 需求 23：金字塔可视化界面

**用户故事：** 作为用户，我希望能够通过可视化界面探索知识金字塔，以便直观了解知识结构。

#### 验收标准

1. WHEN 用户访问金字塔可视化页面 THEN Pyramid_View SHALL 展示可交互的金字塔结构图
2. WHEN 用户点击节点 THEN Pyramid_View SHALL 高亮该节点并展示节点详情面板
3. WHEN 用户展开节点 THEN Pyramid_View SHALL 显示该节点的子节点
4. WHEN 用户折叠节点 THEN Pyramid_View SHALL 隐藏该节点的子节点
5. WHEN 用户拖拽画布 THEN Pyramid_View SHALL 平移视图
6. WHEN 用户缩放画布 THEN Pyramid_View SHALL 调整视图缩放级别
7. WHEN 用户切换金字塔 THEN Pyramid_View SHALL 加载并展示选中金字塔的结构
8. THE Pyramid_View SHALL 使用颜色编码显示节点健康度
9. THE Pyramid_View SHALL 显示节点间的关联关系连线

### 需求 24：信息源管理界面

**用户故事：** 作为管理员，我希望能够通过界面管理所有信息源，以便维护信息获取渠道。

#### 验收标准

1. WHEN 管理员访问信息源管理页面 THEN Source_Management_View SHALL 展示所有信息源的列表视图
2. WHEN 管理员查看信息源列表 THEN Source_Management_View SHALL 显示名称、类型、状态、健康度、最后更新时间
3. WHEN 管理员点击信息源 THEN Source_Management_View SHALL 展示详细配置和历史抓取记录
4. WHEN 管理员添加信息源 THEN Source_Management_View SHALL 展示配置表单，根据类型显示不同字段
5. WHEN 管理员编辑信息源 THEN Source_Management_View SHALL 展示可编辑的配置表单
6. WHEN 管理员测试信息源 THEN Source_Management_View SHALL 执行测试抓取并展示结果预览
7. THE Source_Management_View SHALL 支持按类型、状态、健康度筛选信息源
8. THE Source_Management_View SHALL 显示信息源健康度趋势图

### 需求 25：审批中心界面

**用户故事：** 作为管理员，我希望能够通过审批中心处理所有变更提案，以便高效管理系统进化。

#### 验收标准

1. WHEN 管理员访问审批中心 THEN Approval_Center_View SHALL 展示待审批提案的队列
2. WHEN 管理员查看提案列表 THEN Approval_Center_View SHALL 显示提案类型、标题、提交时间、优先级
3. WHEN 管理员点击提案 THEN Approval_Center_View SHALL 展示提案详情、变更预览和影响分析
4. WHEN 管理员批准提案 THEN Approval_Center_View SHALL 执行变更并显示执行结果
5. WHEN 管理员拒绝提案 THEN Approval_Center_View SHALL 弹出拒绝原因输入框
6. WHEN 管理员修改提案 THEN Approval_Center_View SHALL 展示可编辑的提案内容表单
7. WHEN 管理员查看历史 THEN Approval_Center_View SHALL 展示已处理提案的历史记录
8. THE Approval_Center_View SHALL 显示待审批提案数量的徽章提示

### 需求 26：健康报告界面

**用户故事：** 作为管理员，我希望能够查看系统健康报告，以便了解系统整体状态和问题。

#### 验收标准

1. WHEN 管理员访问健康报告页面 THEN Health_Report_View SHALL 展示系统整体健康评分
2. WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示各金字塔的健康度评分和趋势
3. WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示信息源健康状况汇总
4. WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示热点话题生命周期分布
5. WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示内容抓取和校验的统计数据
6. WHEN 管理员查看报告 THEN Health_Report_View SHALL 展示审批队列积压情况
7. WHEN 存在健康问题 THEN Health_Report_View SHALL 高亮显示问题项并提供改进建议链接
8. THE Health_Report_View SHALL 支持选择时间范围查看历史数据

### 需求 27：数据持久化

**用户故事：** 作为系统，我需要可靠地存储所有数据，以便保证数据的完整性和可恢复性。

#### 验收标准

1. THE Database_Service SHALL 使用 PostgreSQL（生产环境）或 SQLite（开发环境）存储所有结构化数据
2. WHEN 数据写入操作发生 THEN Database_Service SHALL 使用事务确保数据一致性
3. WHEN 查询金字塔结构 THEN Database_Service SHALL 使用递归查询高效返回层级关系数据
4. WHEN 查询内容列表 THEN Database_Service SHALL 支持分页、排序和多条件过滤
5. WHEN 查询历史记录 THEN Database_Service SHALL 支持时间范围查询和变更类型过滤
6. THE Database_Service SHALL 为常用查询字段建立索引
7. THE Database_Service SHALL 支持数据库迁移和版本管理
8. THE Database_Service SHALL 实现软删除机制，保留删除记录的历史

### 需求 28：AI 服务集成

**用户故事：** 作为系统，我需要集成 AI 服务来实现智能化功能，以便提供高质量的内容分析和建议。

#### 验收标准

1. THE AI_Service_Client SHALL 通过硅基流动 API 调用大语言模型服务
2. WHEN 调用 AI 服务 THEN AI_Service_Client SHALL 使用结构化的 prompt 模板
3. WHEN 调用 AI 服务进行内容质量评估 THEN AI_Service_Client SHALL 返回包含各维度分数和评语的结构化结果
4. WHEN 调用 AI 服务生成摘要 THEN AI_Service_Client SHALL 返回指定长度范围内的摘要文本
5. WHEN 调用 AI 服务提取概念 THEN AI_Service_Client SHALL 返回概念列表，每项包含名称、类型、置信度
6. WHEN 调用 AI 服务生成变更建议 THEN AI_Service_Client SHALL 返回结构化的 Change_Proposal 对象
7. IF AI 服务调用失败 THEN AI_Service_Client SHALL 实现指数退避重试机制
8. IF AI 服务持续不可用 THEN AI_Service_Client SHALL 将任务加入待处理队列并通知管理员
9. THE AI_Service_Client SHALL 记录所有 AI 调用的输入、输出和耗时用于调试和优化

### 需求 29：系统配置管理

**用户故事：** 作为管理员，我希望能够配置系统的各项参数，以便根据需要调整系统行为。

#### 验收标准

1. THE Configuration_Service SHALL 支持通过环境变量配置敏感信息（API 密钥、数据库连接等）
2. THE Configuration_Service SHALL 支持通过配置文件配置业务参数
3. WHEN 管理员修改配置 THEN Configuration_Service SHALL 验证配置值的有效性
4. WHEN 配置变更 THEN Configuration_Service SHALL 记录变更历史
5. THE Configuration_Service SHALL 提供以下可配置项：
   - 抓取频率范围和默认值
   - 校验阈值（质量分数、置信度等）
   - 健康度评估阈值
   - AI 服务参数（模型、温度、最大 token 等）
   - 重试策略参数
6. THE Configuration_Service SHALL 支持配置的热更新（无需重启）

### 需求 30：日志与监控

**用户故事：** 作为管理员，我希望能够查看系统运行日志和监控指标，以便排查问题和优化性能。

#### 验收标准

1. THE Logging_Service SHALL 记录所有关键操作的日志，包含时间戳、操作类型、操作者、结果
2. THE Logging_Service SHALL 支持不同日志级别（DEBUG、INFO、WARNING、ERROR）
3. THE Logging_Service SHALL 将日志输出到文件和控制台
4. WHEN 发生错误 THEN Logging_Service SHALL 记录完整的错误堆栈和上下文信息
5. THE Monitoring_Service SHALL 收集系统性能指标（API 响应时间、数据库查询时间、AI 调用耗时）
6. THE Monitoring_Service SHALL 收集业务指标（抓取数量、校验通过率、审批处理速度）
7. THE Monitoring_Service SHALL 提供指标查询 API 供健康报告使用

### 需求 31：API 接口设计

**用户故事：** 作为前端开发者，我需要清晰的 API 接口，以便实现前后端分离的架构。

#### 验收标准

1. THE API_Service SHALL 使用 RESTful 风格设计接口
2. THE API_Service SHALL 为所有接口提供 OpenAPI/Swagger 文档
3. WHEN 请求成功 THEN API_Service SHALL 返回统一格式的成功响应
4. WHEN 请求失败 THEN API_Service SHALL 返回统一格式的错误响应，包含错误码和错误信息
5. THE API_Service SHALL 实现请求参数验证
6. THE API_Service SHALL 支持 CORS 跨域请求
7. THE API_Service SHALL 实现基本的认证机制（开发阶段可简化）
8. THE API_Service SHALL 对敏感操作实现速率限制

### 需求 32：迭代开发支持

**用户故事：** 作为开发者，我希望系统支持渐进式开发，以便按迭代计划逐步完善功能。

#### 验收标准

1. THE System_Architecture SHALL 支持模块化设计，各模块可独立开发和测试
2. THE System_Architecture SHALL 定义清晰的模块接口，支持模块间松耦合
3. THE System_Architecture SHALL 支持功能开关，可在运行时启用/禁用特定功能
4. THE Database_Schema SHALL 支持向后兼容的迁移
5. THE API_Service SHALL 支持 API 版本管理
6. THE System_Architecture SHALL 支持本地开发环境快速启动
7. THE System_Architecture SHALL 提供 Docker Compose 配置用于后续容器化部署

### 需求 33：信息源与金字塔节点关联

**用户故事：** 作为系统，我需要维护信息源与金字塔节点的关联关系，以便将抓取的内容正确分类。

#### 验收标准

1. WHEN 管理员关联信息源到节点 THEN Source_Node_Mapper SHALL 建立信息源与一个或多个 Pyramid_Node 的映射关系
2. WHEN 管理员解除关联 THEN Source_Node_Mapper SHALL 移除指定的映射关系
3. WHEN 查询节点关联的信息源 THEN Source_Node_Mapper SHALL 返回该节点直接关联和继承关联的所有信息源
4. WHEN 查询信息源关联的节点 THEN Source_Node_Mapper SHALL 返回该信息源关联的所有节点列表
5. WHEN 节点被删除 THEN Source_Node_Mapper SHALL 自动清理相关的映射关系
6. THE Source_Node_Mapper SHALL 支持关联权重设置，表示信息源与节点的相关程度

### 需求 34：内容去重与更新检测

**用户故事：** 作为系统，我需要识别重复内容和内容更新，以便避免冗余存储和保持内容最新。

#### 验收标准

1. WHEN 新内容进入系统 THEN Deduplication_Service SHALL 计算内容的特征指纹
2. WHEN 检测到相同指纹 THEN Deduplication_Service SHALL 标记为重复内容并关联到原始内容
3. WHEN 检测到相似内容 THEN Deduplication_Service SHALL 调用 AI 判断是否为同一内容的不同版本
4. WHEN 确认为内容更新 THEN Deduplication_Service SHALL 更新原始内容并保留版本历史
5. THE Deduplication_Service SHALL 支持配置相似度阈值
6. THE Deduplication_Service SHALL 记录去重决策的依据

### 需求 35：域名白名单管理

**用户故事：** 作为管理员，我希望能够管理可信域名白名单，以便控制信息来源的可信度。

#### 验收标准

1. WHEN 管理员添加域名到白名单 THEN Whitelist_Manager SHALL 创建包含域名、可信等级、添加原因的记录
2. WHEN 管理员移除域名 THEN Whitelist_Manager SHALL 将域名从白名单移除并记录移除原因
3. WHEN 管理员编辑域名信息 THEN Whitelist_Manager SHALL 更新域名的可信等级和备注
4. WHEN 硬性校验检查域名 THEN Whitelist_Manager SHALL 返回域名是否在白名单及其可信等级
5. THE Whitelist_Manager SHALL 预置常见权威域名（arXiv、GitHub、官方博客等）
6. THE Whitelist_Manager SHALL 支持域名通配符匹配（如 *.openai.com）

### 需求 36：内容原文存储与访问

**用户故事：** 作为用户，我希望能够访问内容的原文，以便获取完整信息。

#### 验收标准

1. WHEN 内容被抓取 THEN Content_Storage_Service SHALL 存储内容的原始 URL
2. WHEN 内容被抓取 THEN Content_Storage_Service SHALL 可选存储内容的快照副本
3. WHEN 用户请求原文 THEN Content_Storage_Service SHALL 优先返回原始 URL
4. IF 原始 URL 不可访问 THEN Content_Storage_Service SHALL 返回存储的快照副本
5. THE Content_Storage_Service SHALL 定期检查原始 URL 的可访问性
6. THE Content_Storage_Service SHALL 支持配置是否存储快照副本

### 需求 37：用户贡献追踪

**用户故事：** 作为系统，我需要追踪用户贡献的内容，以便评估贡献质量和给予认可。

#### 验收标准

1. WHEN 用户提交内容 THEN Contribution_Tracker SHALL 记录提交者、提交时间、内容标识
2. WHEN 用户贡献通过校验 THEN Contribution_Tracker SHALL 更新贡献状态为"已采纳"
3. WHEN 用户贡献被拒绝 THEN Contribution_Tracker SHALL 更新贡献状态为"已拒绝"并记录原因
4. WHEN 查询用户贡献历史 THEN Contribution_Tracker SHALL 返回该用户的所有贡献记录和状态
5. THE Contribution_Tracker SHALL 统计用户的贡献数量和采纳率
6. THE Contribution_Tracker SHALL 支持匿名贡献（不记录用户身份）

### 需求 38：金字塔模板系统

**用户故事：** 作为管理员，我希望能够使用预设模板快速创建金字塔，以便快速启动知识组织。

#### 验收标准

1. THE Template_Service SHALL 提供以下预设金字塔模板：
   - AI 开发工具链（IDE、框架、库、部署工具等）
   - Agent 生态（Agent 框架、工具调用、多 Agent 协作等）
   - Prompt 工程（提示词技术、优化方法、评估方法等）
   - 模型应用能力（文本生成、代码生成、多模态等）
   - 热点追踪（新模型发布、重大更新、行业动态等）
2. WHEN 管理员选择模板创建金字塔 THEN Template_Service SHALL 基于模板创建完整的节点结构
3. WHEN 管理员自定义模板 THEN Template_Service SHALL 保存自定义模板供后续使用
4. THE Template_Service SHALL 支持模板的导入和导出

### 需求 39：批量操作支持

**用户故事：** 作为管理员，我希望能够批量执行操作，以便提高管理效率。

#### 验收标准

1. WHEN 管理员批量审批提案 THEN Batch_Operation_Service SHALL 按顺序执行所有选中提案的审批
2. WHEN 管理员批量删除内容 THEN Batch_Operation_Service SHALL 删除所有选中的内容
3. WHEN 管理员批量移动内容 THEN Batch_Operation_Service SHALL 将所有选中内容移动到目标节点
4. WHEN 管理员批量更新信息源状态 THEN Batch_Operation_Service SHALL 更新所有选中信息源的状态
5. IF 批量操作中某项失败 THEN Batch_Operation_Service SHALL 记录失败项并继续执行其余操作
6. THE Batch_Operation_Service SHALL 返回批量操作的执行结果汇总

### 需求 40：搜索与过滤系统

**用户故事：** 作为用户，我希望能够快速搜索和过滤内容，以便找到需要的信息。

#### 验收标准

1. WHEN 用户执行全文搜索 THEN Search_Service SHALL 在标题、摘要、标签中搜索关键词
2. WHEN 用户执行高级搜索 THEN Search_Service SHALL 支持布尔运算符（AND、OR、NOT）
3. WHEN 用户按金字塔节点过滤 THEN Search_Service SHALL 返回该节点及其子节点下的所有内容
4. WHEN 用户按时间范围过滤 THEN Search_Service SHALL 返回指定时间范围内的内容
5. WHEN 用户按质量分数过滤 THEN Search_Service SHALL 返回分数高于阈值的内容
6. WHEN 用户按验证状态过滤 THEN Search_Service SHALL 返回指定验证状态的内容
7. THE Search_Service SHALL 支持搜索结果的排序（相关度、时间、质量分数）
8. THE Search_Service SHALL 高亮显示搜索关键词

### 需求 41：通知系统

**用户故事：** 作为管理员，我希望能够收到重要事件的通知，以便及时响应。

#### 验收标准

1. WHEN 新提案加入审批队列 THEN Notification_Service SHALL 发送通知给管理员
2. WHEN 信息源健康状态变为异常 THEN Notification_Service SHALL 发送告警通知
3. WHEN 系统健康检测发现问题 THEN Notification_Service SHALL 发送健康报告通知
4. WHEN AI 服务持续不可用 THEN Notification_Service SHALL 发送紧急告警
5. THE Notification_Service SHALL 支持通知渠道配置（系统内通知、邮件等）
6. THE Notification_Service SHALL 支持通知级别配置（信息、警告、紧急）
7. THE Notification_Service SHALL 支持通知静默时段设置

### 需求 42：数据导入导出

**用户故事：** 作为管理员，我希望能够导入导出数据，以便数据迁移和备份。

#### 验收标准

1. WHEN 管理员导出金字塔 THEN Export_Service SHALL 生成包含完整结构和内容的 JSON 文件
2. WHEN 管理员导出信息源配置 THEN Export_Service SHALL 生成信息源配置的 JSON 文件
3. WHEN 管理员导入金字塔 THEN Import_Service SHALL 解析 JSON 并创建金字塔结构
4. WHEN 管理员导入信息源配置 THEN Import_Service SHALL 解析 JSON 并创建信息源记录
5. IF 导入数据与现有数据冲突 THEN Import_Service SHALL 提示冲突并提供解决选项
6. THE Export_Service SHALL 支持选择性导出（仅结构/包含内容）
7. THE Import_Service SHALL 验证导入数据的格式和完整性

### 需求 43：变更影响分析

**用户故事：** 作为管理员，我希望在审批变更前了解其影响范围，以便做出明智的决策。

#### 验收标准

1. WHEN 生成金字塔结构变更提案 THEN Impact_Analyzer SHALL 分析受影响的节点数量
2. WHEN 生成金字塔结构变更提案 THEN Impact_Analyzer SHALL 分析受影响的内容数量
3. WHEN 生成金字塔结构变更提案 THEN Impact_Analyzer SHALL 分析受影响的信息源映射
4. WHEN 生成信息源变更提案 THEN Impact_Analyzer SHALL 分析关联的节点和内容
5. THE Impact_Analyzer SHALL 评估变更的风险等级（低/中/高）
6. THE Impact_Analyzer SHALL 在提案详情中展示完整的影响分析报告

### 需求 44：回滚机制

**用户故事：** 作为管理员，我希望能够回滚错误的变更，以便恢复系统到正确状态。

#### 验收标准

1. WHEN 变更执行完成 THEN Rollback_Service SHALL 保存变更前的状态快照
2. WHEN 管理员请求回滚 THEN Rollback_Service SHALL 恢复到变更前的状态
3. WHEN 回滚执行 THEN Rollback_Service SHALL 记录回滚操作和原因
4. THE Rollback_Service SHALL 支持回滚到指定的历史版本
5. THE Rollback_Service SHALL 在回滚前展示将要恢复的状态预览
6. IF 回滚失败 THEN Rollback_Service SHALL 保持当前状态不变并报告错误

### 需求 45：AI 提示词管理

**用户故事：** 作为管理员，我希望能够管理 AI 服务使用的提示词模板，以便优化 AI 输出质量。

#### 验收标准

1. THE Prompt_Manager SHALL 维护各功能场景的提示词模板：
   - 内容质量评估提示词
   - 摘要生成提示词
   - 概念提取提示词
   - 分类推荐提示词
   - 变更建议生成提示词
2. WHEN 管理员编辑提示词 THEN Prompt_Manager SHALL 保存新版本并保留历史版本
3. WHEN 管理员测试提示词 THEN Prompt_Manager SHALL 使用测试输入执行并返回结果
4. THE Prompt_Manager SHALL 支持提示词的 A/B 测试
5. THE Prompt_Manager SHALL 记录各版本提示词的效果指标

### 需求 46：定时任务管理

**用户故事：** 作为系统，我需要管理各种定时任务，以便自动化执行周期性工作。

#### 验收标准

1. THE Scheduler_Service SHALL 管理以下定时任务：
   - 内容抓取任务（按信息源配置的频率）
   - 信息源健康检查任务（每小时）
   - 系统健康检测任务（每天）
   - 热点生命周期更新任务（每天）
   - 概念漂移检测任务（每周）
2. WHEN 定时任务执行 THEN Scheduler_Service SHALL 记录执行开始时间、结束时间、执行结果
3. WHEN 定时任务失败 THEN Scheduler_Service SHALL 记录错误信息并按策略重试
4. THE Scheduler_Service SHALL 支持手动触发任务执行
5. THE Scheduler_Service SHALL 支持暂停和恢复任务
6. THE Scheduler_Service SHALL 防止同一任务的并发执行

### 需求 47：性能优化

**用户故事：** 作为系统，我需要保持良好的性能，以便提供流畅的用户体验。

#### 验收标准

1. THE Performance_Optimizer SHALL 对金字塔可视化数据实现缓存
2. THE Performance_Optimizer SHALL 对信息流列表实现分页加载
3. THE Performance_Optimizer SHALL 对搜索结果实现缓存
4. WHEN 数据变更 THEN Performance_Optimizer SHALL 自动失效相关缓存
5. THE Performance_Optimizer SHALL 对大量数据的操作实现异步处理
6. THE Performance_Optimizer SHALL 监控 API 响应时间并在超过阈值时告警

### 需求 48：错误处理与恢复

**用户故事：** 作为系统，我需要优雅地处理错误并支持恢复，以便保持系统稳定运行。

#### 验收标准

1. WHEN API 请求发生错误 THEN Error_Handler SHALL 返回结构化的错误响应
2. WHEN 后台任务发生错误 THEN Error_Handler SHALL 记录错误并按策略重试
3. WHEN 数据库操作失败 THEN Error_Handler SHALL 回滚事务并记录错误
4. WHEN AI 服务调用失败 THEN Error_Handler SHALL 将任务加入重试队列
5. THE Error_Handler SHALL 对不同类型的错误采用不同的重试策略
6. THE Error_Handler SHALL 在错误持续发生时触发告警
7. THE Error_Handler SHALL 支持手动重试失败的任务
