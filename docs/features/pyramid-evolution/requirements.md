# Requirements: Pyramid Evolution Engine (金字塔进化引擎)

## Overview

金字塔不是静态的分类树，而是随着信息流（Feed）不断涌入而动态生长的知识架构。本功能旨在让 AI 成为金字塔的“园丁”，通过审视新流入的内容，自动发现结构上的缺失、冗余或过载，并提出**可立即执行**的演进建议。

核心目标：解决“建议无价值”和“建议无法落实”的问题，实现从“内容洞察”到“结构变更”的自动化闭环。

## User Stories

### Story 1: 新概念发现 (New Concept Discovery)

As a 知识库管理员,
I want 系统能识别出新 Feed 中涌现的、当前金字塔尚未覆盖的新概念,
So that 我可以及时扩充金字塔结构，接纳新的知识领域。

**Acceptance Criteria:**

- [ ] AC1: 识别结构缺失
  - **Given**: 系统接收了一批新 Feed（如 20 条），其中包含一个新的技术术语（如 "Mcp Server"），而当前金字塔中没有相关节点。
  - **When**: AI 执行金字塔健康/进化分析。
  - **Then**: 生成一条 `create_node` 类型的建议。
  - **And**: 建议明确指出：“发现新概念 'Mcp Server'，当前结构未覆盖”。

- [ ] AC2: 建议包含完整落地参数
  - **Given**: 生成了新增节点建议。
  - **When**: 用户查看建议详情。
  - **Then**: 建议参数 (`params`) 中必须包含：
    - `parent_id`: 推荐挂载的父节点 ID（AI 根据语义判断最合适的归属）。
    - `name`: 新节点名称（如 "Mcp Protocol"）。
    - `description`: 基于内容的节点描述。
    - `evidence`: 触发该建议的 Feed 标题/摘要样本（作为证据）。

### Story 2: 节点粒度自适应 - 智能拆分 (Smart Split)

As a 知识库管理员,
I want 当某个节点下的内容过于杂乱时，AI 能提供具体的拆分方案,
So that 我可以一键将大节点拆解为更细粒度的子节点。

**Acceptance Criteria:**

- [ ] AC1: 具体的拆分方案
  - **Given**: 节点 "AI Tools" 下积累了 50 条内容，混合了 "LLM", "Image Gen", "Audio" 等不同主题。
  - **When**: AI 生成 `split_node` 建议。
  - **Then**: 建议中**必须**包含具体的子节点规划（`new_children`）：
    - 子节点 1: "Large Language Models" (描述: ...)
    - 子节点 2: "Image Generation" (描述: ...)
    - 子节点 3: "Audio Processing" (描述: ...)
  - **And**: 禁止生成 "建议拆分此节点" 这种空泛的、无执行方案的建议。

- [ ] AC2: 拆分执行自动化
  - **Given**: 用户点击“采纳”拆分建议。
  - **When**: 系统执行建议。
  - **Then**: 自动在原节点下创建 AI 规划好的所有子节点。
  - **And**: 原节点的描述（如有必要）根据剩余范围进行更新。

### Story 3: 节点粒度自适应 - 智能合并 (Smart Merge)

As a 知识库管理员,
I want 当发现多个节点语义重复或内容稀疏时，AI 建议合并它们,
So that 金字塔保持精炼，避免过度碎片化。

**Acceptance Criteria:**

- [ ] AC1: 识别冗余节点
  - **Given**: 存在两个兄弟节点 "Python 教程" 和 "Python Learning"，且内容高度重叠或都很少。
  - **When**: AI 执行分析。
  - **Then**: 生成 `merge_node` 建议，指明源节点列表 (`source_ids`) 和目标节点 (`target_id` 或新节点名)。

### Story 4: 语义增强 (Semantic Enhancement)

As a 系统架构师,
I want 金字塔的每个节点都有准确的、基于内容的描述 (Description),
So that AI 在后续处理（如分类、拆分）时能准确理解该节点的定义和边界，而不是仅靠名字猜测。

**Acceptance Criteria:**

- [ ] AC1: 基于内容的描述生成
  - **Given**: 一个节点只有名字（如 "Agent"），但下面有 10 条关于 "Autonomous Agents" 和 "Multi-Agent Systems" 的内容。
  - **When**: AI 生成 `update_node` 建议或创建新节点时。
  - **Then**: 自动生成描述："关注自主智能体及多智能体系统的架构与协作模式"。
  - **And**: 描述必须反映节点下的实际内容特征，而非仅对名字的扩写。

- [ ] AC2: 描述作为核心上下文
  - **Given**: AI 执行拆分或分类任务。
  - **When**: 构建 Prompt。
  - **Then**: 必须包含节点的 `description` 字段，作为 AI 理解节点语义的主要依据。

### Story 5: 演进闭环与执行 (Evolution Execution)

As a 知识库管理员,
I want 点击“采纳”后系统能自动完成节点创建和层级调整,
So that 我不需要手动去一个个建节点、改名字。

**Acceptance Criteria:**

- [ ] AC1: 自动化执行 `create_node`
  - **Given**: 采纳“新概念发现”建议（包含 `parent_id`, `name`, `description`）。
  - **When**: 执行建议。
  - **Then**: 在指定父节点下创建新节点，写入描述，并记录日志。

- [ ] AC2: 自动化执行 `split_node`
  - **Given**: 采纳“智能拆分”建议（包含 `new_children` 列表）。
  - **When**: 执行建议。
  - **Then**: 批量创建所有子节点。

## Constraints

- **Evidence-Based**: 所有的进化建议必须基于实际存在的 Feed 或 Content 数据，禁止 AI 凭空想象不存在的分类。
- **Non-Destructive**: 拆分操作默认只创建新结构，**不自动移动现有内容**（因为移动内容涉及复杂的分类准确性问题，风险较高，V1 版本先做结构调整，内容由人工或后续的自动分类任务处理）。
- **Human-in-the-Loop**: 所有的结构变更建议必须经过人确认（Accept）才能执行。

## Out of Scope (V1)

- **自动内容重分类 (Auto-Reclassification)**: 拆分节点后，自动将原节点下的 50 条内容分配到新子节点。这需要昂贵的逐条分析，V1 暂不包含，仅做结构调整。
