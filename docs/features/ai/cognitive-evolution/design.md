# Design: Iteration 3 - Cognitive Evolution (认知进化)

## 1. 概述

本迭代旨在赋予系统"认知"能力，通过集成 LLM 和向量检索（Vector Search）实现对多模态输入（文本/URL/文件）的智能理解，提取关键概念，并将其转化为对知识金字塔的结构化变更建议（提案）。同时，建立完整的"贡献-审批-回滚"闭环，确保进化的可控性。

## 2. 核心模块设计

### 2.1 多模态输入处理 (Input Processing)

- **InputProcessor**: 统一处理入口，支持 Text, URL, File。
  - URL: 使用 `CrawlEngine` 抓取内容。
  - File: 提取文本 (支持 TXT/MD/PDF/Image)。
    - OCR 集成: 使用 `AIService` (Vision Capabilities) 处理 PDF/Image。
  - Text: 直接处理。
- **数据流**: Input -> `ContentItem` (DB) -> `ContentAnalyzer`。

### 2.2 智能分析与提案生成 (Analysis & Proposal)

- **ConceptExtractor**: 调用 AI (SiliconFlow API) 从文本中提取 Concept (Name, Type, Description)。
- **ConceptMatcher**:
  - 提取的 Concept vs 现有 Pyramid Nodes。
  - 匹配逻辑: Exact Match -> Synonym Match (基于 `synonym_mappings` 表) -> New Concept。
- **EvolutionEngine (New)**:
  - **Auto-Classification**: 使用向量检索 (`VectorService`) 将内容自动归类到现有节点。
    - 流程: Content Vector -> Semantic Search -> Threshold Check -> Link Content Proposal。
  - **Cluster Discovery**: 发现新节点建议。
    - 流程: Unlinked Contents -> Vector Clustering -> Generate Cluster Summary -> Create Node Proposal。
- **SynonymManager**: 管理同义词库，提升匹配准确率。

### 2.3 审批流与回滚 (Approval & Rollback)

- **ApprovalService**: 管理提案状态 (Pending -> Approved/Rejected)。
- **ImpactAnalyzer**:
  - 评估提案风险等级 (Low/Medium/High)。
  - 识别受影响的节点和关联关系。
  - 计算影响范围 (Impact Scope)。
- **DecisionExecutor**: 执行 Approved 提案。
  - `create_node`: 在 Pyramid 中创建新节点。
  - `link_content`: 建立 `ContentNodeRelation`。
- **SnapshotService**: 执行变更前自动创建金字塔快照 (JSON/DB Dump)。
- **RollbackMechanism**:
  - 记录 `Approval.original_data`。
  - 支持一键回滚：恢复快照 / 逆向操作。

## 3. 数据库模型变更

- **Approval**: 新增 `source_content_id`, `generated_by`, `confidence_score`, `original_data`, `risk_level`, `impact_analysis` (JSON)。
- **Concept**: 新增表，存储提取的原子概念。
- **ConceptSynonym**: 新增表，存储 `term` -> `concept_id` 映射。
- **Contribution**: 记录用户提交，关联 `extracted_concepts` 和 `status`。

## 4. API 设计

### 4.1 Contribution & Analysis
- `POST /api/v1/contents/text`: 提交文本。
- `POST /api/v1/contents/url`: 提交链接。
- `POST /api/v1/contents/upload`: 提交文件。
- `POST /api/v1/contents/{id}/analyze`: 触发 AI 分析，生成提案。
- `GET /api/v1/contributions`: 获取贡献列表。

### 4.2 Synonyms
- `GET /api/v1/synonyms`: 列表。
- `POST /api/v1/synonyms`: 创建。
- `PUT /api/v1/synonyms/{id}`: 更新。
- `DELETE /api/v1/synonyms/{id}`: 删除。
- `POST /api/v1/synonyms/bulk`: 批量导入。

### 4.3 Approvals
- `GET /api/v1/approvals/pending`: 待审批列表。
- `GET /api/v1/approvals/history`: 审批历史。
- `POST /api/v1/approvals/{id}/review`: 批准/拒绝。
- `POST /api/v1/approvals/{id}/execute`: 执行变更。
- `POST /api/v1/approvals/{id}/rollback`: 回滚变更。
- `GET /api/v1/approvals/{id}/impact`: 获取影响分析报告。

### 4.4 Snapshots (Pyramid)
- `GET /api/v1/pyramids/{id}/snapshots`: 获取金字塔历史快照列表。
- `GET /api/v1/pyramids/{id}/snapshots/{snapshot_id}`: 获取快照详情。
- `POST /api/v1/pyramids/{id}/rollback/{snapshot_id}`: 回滚金字塔至指定快照。

## 5. 前端设计

### 5.1 贡献中心 (Contributions)
- **页面**: `/contributions`
- **功能**:
  - 多 Tab 提交入口 (Text/Link/File)。
  - 提交历史列表 (状态：Analyzing, Pending Review, Accepted)。
  - 详情页 (Modal): 查看 AI 分析结果、提取的概念、拒绝原因。

### 5.2 审批中心 (Approval)
- **页面**: `/approval`
- **功能**:
  - 提案卡片流。
  - 风险提示 (High/Medium/Low tags)。
  - 差异对比 (Diff View): 显示新增节点位置/关联关系。
  - 决策操作: Approve / Reject / Edit。
  - 历史视图: 查看已执行提案，支持一键回滚。

### 5.3 同义词管理 (Synonyms)
- **页面**: `/synonyms`
- **功能**:
  - 概念-同义词映射表。
  - 搜索与过滤。
  - 添加/编辑/删除同义词映射。

## 6. 安全与稳定性

- **AI 调用**: 增加重试机制 (Tenacity)，处理 Rate Limit。
- **事务一致性**: 提案执行采用 DB 事务，失败自动回滚。
- **快照**: 每次结构变更前强制快照。
- **向量检索**: 使用 ChromaDB 本地存储，确保隐私和性能。
