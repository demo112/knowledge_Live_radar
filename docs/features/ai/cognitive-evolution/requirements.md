# Requirements: 认知进化 (Cognitive Evolution)

## Overview

Cognitive Evolution 是系统的核心能力，旨在通过 AI 和向量检索赋予系统“理解”能力。它通过分析多模态输入（Text/URL/File），智能提取概念（Concepts），并将其转化为对知识金字塔的结构化变更建议（提案）。同时，建立完整的“贡献-审批-回滚”闭环，确保进化的可控性。

## User Stories

### Story 1: 多模态输入处理 (Input Processing)

As a 用户, I want 能够提交各种格式的知识素材（文本、链接、文件）, So that 系统可以分析并吸收这些知识。

**Acceptance Criteria:**

- [ ] AC1: 统一输入处理
  - **Given**: 用户提交任意类型的内容（Text, URL, File）
  - **When**: 提交 API 调用
  - **Then**: 
    - 系统通过 `InputProcessor` 统一处理
    - 自动提取文本内容 (Web 抓取 / OCR / 文本解析)
    - 存储为标准的 `ContentItem`

- [ ] AC2: OCR 图像识别 (可选)
  - **Given**: 用户上传包含文本的图片或 PDF
  - **When**: 提交文件
  - **Then**: 
    - 调用 `AIService` 的 Vision 能力进行 OCR
    - 提取高精度的文本内容

### Story 2: 智能分析与提案 (Analysis & Proposal)

As a 系统, I want 自动从输入内容中提取概念并生成结构化建议, So that 知识能够自动沉淀到金字塔中。

**Acceptance Criteria:**

- [ ] AC1: 概念提取 (Concept Extraction)
  - **Given**: 一段新的文本内容
  - **When**: 触发 AI 分析
  - **Then**: 
    - 调用 `ConceptExtractor`
    - AI 返回关键概念列表 (Name, Type, Description)
    - 系统根据同义词库 (`SynonymManager`) 进行匹配
    - 识别是新概念还是已知概念

- [ ] AC2: 自动归类建议 (Auto-Classification)
  - **Given**: 提取出的概念与现有节点匹配
  - **When**: 分析完成
  - **Then**: 
    - 生成 `LINK_CONTENT` 类型的提案
    - 建议将该内容关联到匹配的节点
    - 提供 AI 推荐理由

- [ ] AC3: 新节点发现 (Cluster Discovery)
  - **Given**: 多个未关联内容聚焦于同一新概念
  - **When**: 执行聚类分析
  - **Then**: 
    - 生成 `ADD_NODE` 类型的提案
    - 建议创建新节点来承载这些内容

### Story 3: 审批流与回滚 (Approval & Rollback)

As a 管理员, I want 审核所有系统生成的变更提案, So that 我可以控制知识库的质量并防止错误进化。

**Acceptance Criteria:**

- [ ] AC1: 提案审批
  - **Given**: 列表中有一条待审批的提案
  - **When**: 管理员点击“批准”
  - **Then**: 
    - 系统执行变更 (创建节点 / 关联内容)
    - 记录变更日志
    - 提案状态变更为 `APPROVED`

- [ ] AC2: 影响分析与风险提示
  - **Given**: 一个涉及删除或重大结构调整的提案
  - **When**: 查看详情
  - **Then**: 
    - 系统展示受影响的节点和关联数量
    - 标记风险等级 (High/Medium/Low)

- [ ] AC3: 变更回滚
  - **Given**: 一个已执行的错误变更
  - **When**: 管理员点击“回滚”
  - **Then**: 
    - 系统根据快照 (`SnapshotService`) 恢复数据
    - 撤销之前的结构变更
    - 记录回滚操作

## Data Model

- **Approval**: 提案核心表，记录变更类型、原数据、风险等级。
- **Concept**: 原子概念表。
- **ConceptSynonym**: 同义词映射表。
- **Contribution**: 用户贡献记录表。

## Metadata

- 规模: 大
- 涉及模块: `ai-core`, `evolution-engine`, `approval-service`
- 涉及端: Backend, Frontend
- 状态: 规划中 (Draft)
