# Requirements: AI 辅助金字塔进化 (Pyramid Evolution)

## Overview

利用 AI 提取的 "概念" (Concepts) 和 "标签" (Tags)，自动化维护和演进知识金字塔结构。系统将自动发现新节点、建立节点关联，并协助管理员对内容进行归类。所有的结构变更都以 "提案" (Proposal) 的形式生成，遵循 Human-in-the-loop 原则。

## User Stories

### Story 1: 智能归类 (Auto Classification)

As a 系统, I want 自动将新抓取的内容归类到现有的金字塔节点, so that 减少人工分类成本，确保内容有序组织。

**Acceptance Criteria:**

- [ ] AC1: 基于概念匹配的归类
  - **Given**: 一条新内容已完成 AI 处理（提取了 concepts），且系统中存在金字塔结构
  - **When**: 执行归类任务（实时或定时）
  - **Then**: 
    - 计算内容概念与现有节点名称/描述的语义相似度
    - 若相似度 > 0.8，自动将内容关联到该节点
    - 记录归类来源为 "AI_AUTO"
    - **同步要求**: 确保 `content_node_relations` 表正确插入记录，且更新节点的 `content_count` 等统计信息。

- [ ] AC2: 归类不确定处理
  - **Given**: 内容概念与所有节点的相似度均 < 0.8 但 > 0.5
  - **When**: 执行归类任务
  - **Then**: 
    - 不执行自动关联
    - 生成一个 `CLASSIFY_CONTENT` 类型的建议（或在管理端标记为 "待确认"）
    - 推荐 Top 3 可能的节点供管理员选择

### Story 2: 发现新节点 (Concept Clustering)

As a 管理员, I want 系统自动发现未被覆盖的高频新概念, so that 我可以及时创建新节点来承载这些知识。

**Acceptance Criteria:**

- [ ] AC1: 孤立内容聚类
  - **Given**: 系统中有一批未关联任何金字塔节点的内容（孤立内容）
  - **When**: 执行 "结构进化分析" 定时任务（如每晚）
  - **Then**: 
    - 系统分析孤立内容中的 Concept 分布
    - 识别出出现频率 > 5 次且语义相近的概念簇（Cluster）

- [ ] AC2: 生成新增节点提案
  - **Given**: 识别出一个高频概念簇（例如 "MCP" 出现了 10 次）
  - **When**: 分析任务完成
  - **Then**: 
    - 生成 `ADD_NODE` 类型的审批提案
    - 提案包含：建议节点名称（如 "MCP"）、建议父节点（基于语义分析）、关联的孤立内容列表
    - AI 提供推荐理由："发现 10 篇未归类文章聚焦于此概念"
    - **同步要求**: 提案被批准后，系统必须自动创建新节点，并**立即**将提案中列出的孤立内容关联到该新节点。

### Story 3: 建立节点关联 (Semantic Linking)

As a 系统, I want 发现现有节点之间的隐含关系, so that 构建更密集的知识网络。

**Acceptance Criteria:**

- [ ] AC1: 基于共现的关联发现
  - **Given**: 两个不同的节点 A 和 B
  - **When**: 执行 "结构进化分析" 任务
  - **Then**: 
    - 统计同时属于 A 和 B 的内容数量，或 A 和 B 共享相同 Concept 的程度
    - 若关联强度超过阈值，且当前无显式关联
    - 生成 `LINK_NODES` 提案，建议建立 "相关" 关系

### Story 4: 按需结构分析 (On-Demand Analysis)

As a 管理员, I want 随时触发指定金字塔的结构分析, So that 我可以立即获取优化建议，而不必等待定时任务。

**Acceptance Criteria:**

- [ ] AC1: 手动触发分析 API
  - **Given**: 用户在前端查看某个金字塔
  - **When**: 点击“分析金字塔”按钮（调用 `POST /api/v1/pyramids/{id}/analyze`）
  - **Then**: 
    - 系统立即启动异步分析任务
    - 返回任务 ID
    - 前端显示“分析中...”状态

- [ ] AC2: 获取实时建议
  - **Given**: 分析任务完成
  - **When**: 前端轮询或收到通知
  - **Then**: 
    - 用户界面刷新，显示最新的优化建议列表（如新增节点、拆分节点等）

### Story 5: 建议的采纳与拒绝 (Apply/Reject)

As a 管理员, I want 在前端直接处理优化建议, So that 我可以快速迭代金字塔结构。

**Acceptance Criteria:**

- [ ] AC1: 采纳建议
  - **Given**: 列表中有一条“新增节点”建议
  - **When**: 用户点击“采纳”
  - **Then**: 
    - 系统自动执行该建议（创建节点、关联内容）
    - 建议状态变更为 `ACCEPTED`
    - 前端移除该建议项

- [ ] AC2: 拒绝建议
  - **Given**: 列表中有一条建议
  - **When**: 用户点击“拒绝”
  - **Then**: 
    - 建议状态变更为 `REJECTED`
    - 系统记录拒绝原因（可选）
    - 该建议在未来一段时间内不再重复生成

## Constraints

- **审批机制**: 所有结构变更（增删改节点、建立关联）必须生成提案，**严禁 AI 直接修改金字塔结构**。
- **数据一致性**: 节点与内容的关联关系必须保持强一致性。任何节点变更（新增/删除）都必须同步更新关联表，防止出现孤立关联或死链。
- **性能**: 聚类分析可能消耗较多计算资源，应在低峰期（如凌晨）执行。
- **Token 消耗**: 尽量利用本地算法（如基于 Embedding 的相似度计算）减少对昂贵 LLM 的调用，仅在生成最终提案描述时调用 LLM。

## Out of Scope

- **节点拆分/合并**: 本次迭代暂不实现复杂的节点拆分（Split）和合并（Merge）建议，优先实现新增（Add）和关联（Link）。

## Assumptions

- 所有的内容已经经过了 `ContentProcessor` 的处理，具备 `concepts` 和 `tags` 数据。
- 数据库中已存在基础的金字塔结构。
- 我们可以使用 `pgvector` (PostgreSQL) 或本地向量库 (FAISS/Chroma) 或简单的余弦相似度（如果数据量小）来进行相似度计算。**本次迭代假设使用简单的内存计算或 SQL 查询，暂不引入重型向量库。**

## Metadata

- 规模: 中
- 涉及模块: `evolution_engine`, `approval_service`, `node_service`, `pyramid_service`
- 涉及端: Backend, Frontend
- 创建时间: 2026-02-13
- 更新时间: 2026-02-19
- 状态: 已确认
