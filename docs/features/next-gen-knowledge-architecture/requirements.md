# 下一代知识架构：知识图谱簇 + AI 认知模型 + 意图式创建

> **版本**: v2.0
> **创建时间**: 2026-02-20
> **状态**: 草稿
> **性质**: 架构级重构，完全替换现有金字塔体系
> **竞品参考**: [Feedly AI Model](https://feedly.com), [NBot](https://nbot.ai), [Recall](https://getrecall.ai)

## 1. 概述

本特性是 AI Radar 的架构级重构，**完全废弃现有的金字塔（Pyramid）体系**，用知识图谱簇（Knowledge Graph Cluster）替代。

### 1.1 废弃清单

以下概念和功能将被完全移除：

| 废弃项 | 原因 |
|--------|------|
| `pyramids` 表 | 被 `knowledge_clusters` 替代 |
| `pyramid_nodes` 表 | 被 `knowledge_nodes` 替代（去掉 pyramid_id、parent_id、level、path 等树状字段） |
| `PyramidNode.parent_id` 层级关系 | 节点间关系全部由 `node_relations` 图谱边表达 |
| 物化路径 (`path` 字段) | 图谱不需要树状路径 |
| `sort_order` 排序 | 图谱中节点位置由关系权重和布局算法决定 |
| 金字塔视图 | 不再提供树状层级浏览，改为图谱视图 + 簇视图 |
| 金字塔进化功能 (`pyramid-evolution`) | 被簇进化和认知模型进化替代 |
| 金字塔健康度 | 被节点健康度 + 簇健康度替代 |

### 1.2 新架构三大支柱

| # | 支柱 | 借鉴来源 | 定位 |
|---|------|----------|------|
| 1 | 知识图谱簇 | Recall | 核心数据结构，替代金字塔 |
| 2 | AI 认知模型 | Feedly | 每个节点/簇的"理解能力"，替代关键词/向量匹配 |
| 3 | 意图式创建 | NBot | 用户交互入口，替代手动创建流程 |

三者关系：
```
意图式创建（入口）→ AI 认知模型（理解能力）→ 知识图谱簇（组织结构）
```

---

## 2. 核心数据模型

### 2.1 总览

```
knowledge_clusters (知识簇)
    ↕ cluster_node_memberships (多对多)
knowledge_nodes (知识节点，原 pyramid_nodes 的替代)
    ↕ node_relations (图谱边，带类型/权重/证据)
    ↕ content_node_relations (内容关联，保留)
    → concepts (概念注册表，保留并打通)

废弃: pyramids, pyramid_nodes.parent_id/level/path/sort_order/pyramid_id
```

### 2.2 knowledge_nodes（替代 pyramid_nodes）

```sql
CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    node_type VARCHAR(50) DEFAULT 'concept',  -- concept, technology, tool, method, organization
    
    -- AI 认知模型（核心新增）
    ai_model JSONB,
    
    -- 打通 Concept 体系
    concept_id UUID REFERENCES concepts(id),
    
    -- 统计与健康
    health_score INTEGER DEFAULT 100,
    content_count INTEGER DEFAULT 0,
    last_content_at TIMESTAMPTZ,
    
    -- 元数据
    status VARCHAR(20) DEFAULT 'active',      -- active, archived
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);
```

与 `pyramid_nodes` 的关键区别：
- **去掉** `pyramid_id`：节点不再属于某个金字塔
- **去掉** `parent_id`、`level`、`path`、`sort_order`：不再有树状层级
- **新增** `ai_model`：节点级 AI 认知模型
- **新增** `concept_id`：直接关联概念注册表

### 2.3 knowledge_clusters（替代 pyramids）

```sql
CREATE TABLE knowledge_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cluster_type VARCHAR(20) NOT NULL DEFAULT 'manual',  -- manual, ai_generated, intent_created
    center_node_id UUID REFERENCES knowledge_nodes(id),
    
    -- 簇级 AI 认知模型
    ai_model JSONB,
    
    -- 簇特征
    metadata JSONB,           -- AI 生成的簇特征摘要
    health_score INTEGER DEFAULT 100,
    node_count INTEGER DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.4 cluster_node_memberships（新增）

```sql
CREATE TABLE cluster_node_memberships (
    cluster_id UUID REFERENCES knowledge_clusters(id) ON DELETE CASCADE,
    node_id UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',    -- center, member, peripheral
    weight FLOAT DEFAULT 1.0,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (cluster_id, node_id)
);
```

### 2.5 node_relations（升级）

```sql
CREATE TABLE node_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_node_id UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    target_node_id UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    
    -- 关系语义（核心升级）
    relation_type VARCHAR(50) NOT NULL,
    -- 类型枚举: related_to, is_part_of, depends_on, evolved_from,
    --          contradicts, implements, extends, alternative_to
    
    weight FLOAT DEFAULT 1.0,              -- 关系强度
    confidence FLOAT DEFAULT 1.0,          -- AI 置信度
    evidence JSONB,                        -- 关系证据（哪些内容支撑了这个关系）
    discovered_by VARCHAR(20) DEFAULT 'manual',  -- manual, ai_auto, ai_confirm
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source_node_id, target_node_id, relation_type)
);
```

### 2.6 保留并适配的表

| 表 | 变更 |
|----|------|
| `content_items` | 不变 |
| `content_node_relations` | FK 从 `pyramid_nodes` 改为 `knowledge_nodes` |
| `source_node_relations` | FK 从 `pyramid_nodes` 改为 `knowledge_nodes` |
| `concepts` | 保留，通过 `knowledge_nodes.concept_id` 打通 |
| `concept_synonyms` | 保留，数据合并到 ai_model.aliases |
| `concept_definitions` | 保留，数据合并到 ai_model.definition |
| `change_proposals` | `target_id` 指向 `knowledge_nodes` 或 `knowledge_clusters` |
| `information_sources` | 不变 |
| `validation_results` | 不变 |

---

## 3. AI 认知模型 (AI Cognitive Model)

### 3.1 定义

AI 认知模型是附着在每个节点和簇上的"理解能力"。它不是关键词列表，而是一个结构化的语义描述，让 AI 能判断"一篇文章是否在讨论这个概念"。

### 3.2 节点级认知模型结构

```json
{
  "core_identity": "Model Context Protocol",
  "definition": "一种开放标准协议，用于连接 AI 模型与外部工具和数据源",
  "aliases": ["MCP", "模型上下文协议"],
  "context_signals": ["protocol", "server", "client", "tool use", "stdio", "SSE transport"],
  "disambiguation": {
    "exclude": ["Microsoft Certified Professional", "Master Control Program"],
    "confirm_signals": ["出现 protocol + AI/LLM 上下文", "提到 Anthropic 或 Claude"]
  },
  "related_concepts": ["Function Calling", "Tool Use", "Claude", "Anthropic"],
  "scope_boundary": "关于 MCP 协议本身的设计、实现、使用，而非仅仅提到 MCP 的文章",
  "version": 1,
  "last_updated": "2026-02-20"
}
```

### 3.3 簇级认知模型结构

```json
{
  "core_identity": "AI 工具链与协议生态",
  "scope_definition": "覆盖 AI 应用中的工具调用协议、框架集成、Agent 编排",
  "boundary_rules": [
    "包含：工具调用协议、Agent 框架、编排引擎",
    "排除：纯模型训练、硬件优化、学术理论"
  ],
  "member_concepts_summary": ["MCP", "Function Calling", "LangChain", "CrewAI", "AutoGen"],
  "version": 1,
  "last_updated": "2026-02-20"
}
```

簇级模型从成员节点的认知模型自动聚合生成，不需要手动维护。

### 3.4 与现有 Concept 体系的整合

不删除现有 Concept 表，而是将其作为"概念注册表"：

```
Concept (name, type)             → 概念的唯一注册源
ConceptSynonym (synonym)         → 数据同步到 ai_model.aliases
ConceptDefinition (definition)   → 数据同步到 ai_model.definition + scope_boundary

knowledge_nodes.concept_id       → 关联到 Concept
knowledge_nodes.ai_model         → 从 Concept + Synonym + Definition 自动聚合生成
```

当 Concept 相关数据变更时，触发对应节点 ai_model 的重新生成。

### 3.5 用户故事

#### Story 1: 基于认知模型的三阶段分类

As a 系统, I want 使用认知模型进行内容分类, So that 实现概念理解级别的精确分类。

**分类执行路径（三阶段）：**

```
阶段 1: 向量粗筛（成本低，速度快）
├── 将文章 embedding 与所有簇级认知模型的 embedding 做余弦相似度
├── 取 top-3 命中簇（阈值 > 0.5）
├── 再与命中簇下所有节点的 embedding 做相似度
├── 取 top-5 候选节点（阈值 > 0.6）
└── 无任何命中 → 标记为"全局孤立内容"，流程结束

阶段 2: 规则引擎精筛（成本零，速度快）
├── 对 top-5 候选节点，用认知模型中的结构化规则做二次过滤：
│   ├── aliases 匹配：文章中是否出现节点的别名
│   ├── context_signals 命中：文章中出现了多少个上下文信号词
│   ├── disambiguation 排除：是否命中排除规则
│   └── 综合打分 = 向量相似度 × 0.4 + 别名命中 × 0.3 + 信号词覆盖率 × 0.3
├── 得分 > 0.8 → 直接分类（高置信度，不需要 LLM）
├── 得分 0.5-0.8 → 进入阶段 3（需要 LLM 消歧）
└── 得分 < 0.5 → 排除该候选

阶段 3: LLM 消歧（成本高，仅用于模糊案例）
├── 仅对阶段 2 中得分 0.5-0.8 的候选调用 LLM
├── 将文章摘要 + 候选节点的完整认知模型 JSON 组装成 prompt
├── LLM 判断："这篇文章是否在讨论 [节点概念]？"
├── 返回：是/否 + 推理过程 + 置信度
└── 预期：80% 的文章在阶段 2 就能确定，只有 20% 需要 LLM
```

**各阶段的角色说明：**
- 向量匹配没有被"替换"，而是降级为第一道过滤器，负责缩小候选范围
- 认知模型的结构化字段（aliases、context_signals、disambiguation）被编译成规则引擎，负责大部分日常分类
- LLM 只在规则引擎无法确定时介入，负责处理模糊和消歧案例

**Acceptance Criteria:**

- [ ] AC1: 三阶段分类流程
  - **Given**: 一篇新文章进入系统
  - **When**: 执行内容分类
  - **Then**:
    - 阶段 1 向量粗筛：命中 1-3 个簇，5 个候选节点
    - 阶段 2 规则精筛：高置信度候选直接分类，模糊候选进入阶段 3
    - 阶段 3 LLM 消歧（仅在需要时）：返回最终判断 + 推理过程
    - 返回：分类结果 + 各阶段得分 + 推理过程（如有）

- [ ] AC2: 消歧
  - **Given**: 文章提到 "MCP"，阶段 2 规则引擎发现同时命中 disambiguation.exclude 中的 "Microsoft Certified Professional" 和 confirm_signals 中的 "protocol + AI"
  - **When**: 规则引擎无法确定（得分在 0.5-0.8 之间）
  - **Then**:
    - 进入阶段 3，LLM 基于完整上下文判断
    - "protocol" + "AI" 上下文 → 分类到 "MCP协议" 节点
    - 消歧过程记录在推理日志中

- [ ] AC3: 性能与成本
  - **Given**: 100 个簇、500 个节点
  - **When**: 分类一篇文章
  - **Then**:
    - 阶段 1+2 总时间 < 1 秒（本地计算）
    - 阶段 3（如触发）< 5 秒（LLM 调用）
    - 预期 80% 文章不触发阶段 3，LLM 调用量可控

#### Story 2: 认知模型的自动生成与进化

As a 系统, I want AI 自动生成和更新认知模型, So that 管理员不需要手动维护认知规则。

**Acceptance Criteria:**

- [ ] AC1: 自动生成
  - **Given**: 创建新节点，只有名称和简单描述
  - **When**: 触发认知模型生成
  - **Then**:
    - AI 基于名称、描述、已有 Concept/Synonym 数据生成完整认知模型
    - 结果作为建议展示给管理员确认

- [ ] AC2: 基于反馈进化
  - **Given**: 节点已分类 50 篇内容
  - **When**: 系统分析分类反馈
  - **Then**:
    - 发现新的高频上下文信号
    - 发现新的消歧案例
    - 生成认知模型更新提案

- [ ] AC3: 簇级模型自动聚合
  - **Given**: 簇包含 5 个节点，每个有认知模型
  - **When**: 生成/更新簇级认知模型
  - **Then**: 从成员节点提取共性特征，AI 总结生成簇级模型

---

## 4. 知识图谱簇 (Knowledge Graph Clusters)

### 4.1 核心概念

```
知识图谱簇 (Knowledge Cluster)
├── 一组语义相关节点的动态聚合
├── 可由 AI 自动发现，也可由用户/意图式创建
├── 一个节点可以属于多个簇
├── 每个簇有中心节点和簇级 AI 认知模型
└── 簇是动态的，随内容变化自动调整边界

知识节点 (Knowledge Node)
├── 图谱中的基本单元，代表一个概念/技术/工具
├── 不再有父子层级关系
├── 通过 node_relations 与其他节点建立多种类型的关系
├── 通过 cluster_node_memberships 归属到一个或多个簇
└── 每个节点携带 AI 认知模型

关系 (Node Relation)
├── 节点间的有向边，带类型和权重
├── 类型: related_to, is_part_of, depends_on, evolved_from, contradicts, implements, extends, alternative_to
├── 由 AI 自动发现或用户手动创建
└── 带证据（哪些内容支撑了这个关系）
```

### 4.2 用户故事

#### Story 3: 节点跨簇存在

As a 知识管理员, I want 一个节点可以同时属于多个知识簇, So that 反映知识的真实关联。

**Acceptance Criteria:**

- [ ] AC1: 多簇归属
  - **Given**: 节点 "Prompt Engineering" 与 "AI 工具链" 和 "AI 应用开发" 两个簇都相关
  - **When**: 系统分析节点的内容分布和关联关系
  - **Then**:
    - 节点同时出现在两个簇中，角色可不同（center/member/peripheral）
    - 不产生数据冗余（节点只有一份）

#### Story 4: AI 自动发现簇

As a 系统, I want 自动发现语义相关的节点群并形成知识簇, So that 知识结构能自组织演化。

**Acceptance Criteria:**

- [ ] AC1: 簇发现
  - **Given**: 系统中存在大量节点和内容
  - **When**: 执行簇发现分析
  - **Then**:
    - 基于节点间关联强度、共享内容、概念重叠度聚类
    - 生成 `CREATE_CLUSTER` 提案（簇名、中心节点、成员列表、推理过程）
    - 管理员审批后创建

- [ ] AC2: 簇边界动态调整
  - **Given**: 簇已存在，新内容持续涌入
  - **When**: 部分节点的关联模式发生变化
  - **Then**:
    - 检测到簇边界漂移
    - 生成 `ADJUST_CLUSTER` 提案（添加/移除成员节点）
    - 管理员审批后调整

#### Story 5: 关系自动发现

As a 系统, I want 自动发现节点间的隐含关系, So that 构建更密集的知识网络。

**Acceptance Criteria:**

- [ ] AC1: 基于内容共现的关系发现
  - **Given**: 两个节点 A 和 B
  - **When**: 执行关系发现分析
  - **Then**:
    - 统计同时关联到 A 和 B 的内容数量
    - 分析 A 和 B 的认知模型中的概念重叠
    - 若关联强度超过阈值，生成 `LINK_NODES` 提案
    - 提案包含关系类型建议和证据

#### Story 6: 图谱视图与簇视图

As a 知识管理员, I want 通过图谱和簇两种视图浏览知识结构, So that 从不同角度理解知识全貌。

**Acceptance Criteria:**

- [ ] AC1: 图谱视图
  - **Given**: 用户进入知识管理界面
  - **When**: 选择图谱视图
  - **Then**:
    - 展示节点 + 边的网络图
    - 节点大小反映 content_count
    - 边粗细反映关系权重
    - 支持点击节点查看详情、展开关联节点
    - 支持按簇着色

- [ ] AC2: 簇视图
  - **Given**: 用户选择簇视图
  - **When**: 渲染视图
  - **Then**:
    - 以簇为单位的聚合展示
    - 显示簇间关系（基于成员节点的跨簇关联）
    - 点击簇可展开查看内部节点

---

## 5. 意图式创建 (Intent-Driven Creation)

### 5.1 核心流程

```
Describe → Preview → Refine

1. Describe: 用户用自然语言描述想追踪的领域
2. Preview: AI 生成完整知识结构（节点 + 关系 + 簇 + 认知模型 + 推荐信源），用户预览确认
3. Refine: 创建后通过对话持续调整
```

### 5.2 用户故事

#### Story 7: 一句话创建知识结构

As a 知识管理员, I want 用一句话描述我想追踪的领域, So that AI 自动生成完整的知识图谱结构。

**Acceptance Criteria:**

- [ ] AC1: 意图理解与结构生成
  - **Given**: 用户输入 "我想追踪 MCP 协议的最新进展和生态发展"
  - **When**: 调用意图式创建接口
  - **Then**:
    - AI 识别核心概念（MCP、Model Context Protocol）
    - 生成建议的知识结构：
      - 一组知识节点（MCP 核心、MCP Server、MCP Client、MCP Transport 等）
      - 节点间关系（is_part_of、depends_on 等）
      - 一个知识簇（"MCP 协议生态"）
      - 每个节点的初始 AI 认知模型
      - 推荐信源列表及理由
    - 返回完整预览结构

- [ ] AC2: 上下文感知
  - **Given**: 系统中已存在 "AI 工具链" 簇
  - **When**: 用户输入 "追踪 MCP 协议"
  - **Then**:
    - AI 检测到 MCP 与已有 "AI 工具链" 簇高度相关
    - 建议方案 A：在 "AI 工具链" 簇中新增 MCP 相关节点
    - 建议方案 B：创建独立簇并建立跨簇关联
    - 用户选择方案后执行

- [ ] AC3: 预览与确认
  - **Given**: AI 生成了建议结构
  - **When**: 用户在预览界面查看
  - **Then**:
    - 图谱化展示建议的节点和关系
    - 展示每个节点的认知模型摘要
    - 展示推荐信源及理由
    - 用户可修改任何部分
    - 确认后一键创建

#### Story 8: 对话式持续调整

As a 知识管理员, I want 创建后通过对话调整知识结构, So that 不需要手动操作就能优化追踪范围。

**Acceptance Criteria:**

- [ ] AC1: 对话式调整
  - **Given**: 用户已创建 MCP 相关知识结构
  - **When**: 输入 "少一些新闻类的，多关注技术实现细节"
  - **Then**:
    - AI 理解调整意图
    - 调整信源权重（降低新闻类，提升技术博客）
    - 可能建议新增更细粒度的节点（如 "MCP Server 开发"）
    - 生成变更提案供确认

- [ ] AC2: 反馈学习
  - **Given**: 用户多次拒绝某类内容的分类建议
  - **When**: 系统检测到拒绝模式
  - **Then**:
    - 自动调整相关节点的认知模型（更新消歧规则或边界）
    - 生成调整报告

### 5.3 API 设计

```
POST /api/v1/intent/create          # 提交意图，获取 AI 建议结构
POST /api/v1/intent/confirm         # 确认并执行创建
POST /api/v1/intent/refine          # 对话式调整
```

---

## 6. 内容处理流程（新）

### 6.1 完整流程

```
文章进入系统
    ↓
AI 内容处理（清洗、摘要、概念提取）  ← 保留现有能力
    ↓
阶段 1: 向量粗筛 → 命中 1-3 个簇，top-5 候选节点
    ↓
阶段 2: 规则引擎精筛（aliases + context_signals + disambiguation）
    ↓
├── 高置信度（>0.8）→ 直接分类，建立 content_node_relation
├── 模糊（0.5-0.8）→ 阶段 3: LLM 消歧 → 分类或排除
├── 低置信度（<0.5）→ 排除候选
└── 完全无命中 → 标记为"全局孤立内容"
    ↓
孤立内容积累 → 触发新节点/新簇发现提案
```

### 6.2 与现有内容处理的关系

| 现有能力 | 变化 |
|----------|------|
| AI 内容清洗与摘要 | 保留，不变 |
| 概念提取 (concepts/tags) | 保留，提取结果用于认知模型匹配 |
| 三层校验 (硬/软/交叉) | 保留，不变 |
| 向量相似度分类 | **降级**为三阶段分类的第一阶段（粗筛），不再是唯一分类手段 |
| 内容代谢 | 保留，不变 |
| 信源管理 | 保留，`source_node_relations` FK 改为指向 `knowledge_nodes` |

---

## 7. 协同关系总览

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户交互层                                    │
│                                                                 │
│  意图式创建 ──→ "我想追踪 MCP 协议"                              │
│       │                                                         │
│       ▼                                                         │
│  AI 认知模型 ──→ 理解 "MCP" 是什么，生成认知单元                  │
│       │                                                         │
│       ▼                                                         │
│  知识图谱簇 ──→ 创建节点，归入合适的簇，建立关联                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    内容处理层                                    │
│                                                                 │
│  新文章进入 ──→ 三阶段分类（向量粗筛→规则精筛→LLM消歧）          │
│       │                                                         │
│       ▼                                                         │
│  无匹配节点 ──→ 标记孤立 ──→ 积累后触发新节点/新簇发现            │
│       │                                                         │
│       ▼                                                         │
│  认知模型进化 ──→ 从分类反馈中学习 ──→ 更新消歧规则和上下文信号    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 实施路线图

### 阶段划分

```
Phase 1: 数据模型重构 (1-2 周)
├── 创建 knowledge_nodes、knowledge_clusters、cluster_node_memberships 新表
├── 升级 node_relations（weight, confidence, evidence, 更多 relation_type）
├── 迁移 content_node_relations、source_node_relations 的 FK
├── 编写数据迁移脚本（pyramid_nodes → knowledge_nodes）
├── 废弃 pyramids 表和 pyramid_nodes 的树状字段
└── 交付物：新数据模型就绪，旧数据迁移完成

Phase 2: AI 认知模型 (2-3 周)
├── 认知模型数据结构定义（节点级 + 簇级）
├── 认知模型自动生成服务（基于 Concept + Synonym + Definition）
├── 三阶段分类服务（向量粗筛 + 规则引擎精筛 + LLM 消歧）
├── 认知模型进化服务（基于分类反馈更新）
└── 交付物：认知模型驱动的内容分类上线

Phase 3: 图谱簇管理 (2-3 周)
├── 簇的 CRUD API
├── AI 自动簇发现服务
├── 关系自动发现服务
├── 簇边界动态调整
└── 交付物：知识图谱簇的完整后端能力

Phase 4: 意图式创建 (1-2 周)
├── 意图理解 + 结构生成 API
├── 上下文感知（检测与已有结构的关联）
├── 对话式调整 API
└── 交付物：一句话创建 + 对话式调整

Phase 5: 前端重构 (2-3 周)
├── 图谱视图（节点 + 边的网络图）
├── 簇视图（聚合展示）
├── 意图式创建界面（输入框 + 预览 + 确认）
├── 对话式调整界面
├── 移除所有金字塔相关的前端页面和组件
└── 交付物：完整的新 UI
```

### 风险评估

| 阶段 | 风险 | 缓解 |
|------|------|------|
| Phase 1 | 数据迁移丢失或损坏 | 迁移前全量备份，编写回滚脚本 |
| Phase 2 | 认知模型生成质量不稳定 | LLM 生成 + 人工审核校准，逐步放开自动化 |
| Phase 3 | 簇发现算法准确度 | 所有簇变更走审批流 |
| Phase 4 | 意图理解偏差 | 两阶段交互（suggest → confirm） |
| Phase 5 | 图谱可视化性能 | 分层渲染，限制单次展示节点数（< 500） |

---

## 9. 约束

- **审批机制**: 所有结构变更（创建/调整簇、更新认知模型、建立关系）必须走提案审批流，严禁 AI 直接修改
- **性能**: 三阶段分类中阶段 1+2 < 1 秒，阶段 3（如触发）< 5 秒；图谱视图渲染 < 2 秒（500 节点以内）
- **Token 消耗**: 认知模型生成用 LLM；日常分类阶段 1+2 为本地计算零 Token 消耗，仅阶段 3 消歧调用 LLM（预期 80% 文章不触发）
- **数据迁移**: 必须提供 pyramid → knowledge_node 的完整迁移脚本和回滚方案

## 10. 成功指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 内容分类准确率 | >85% | 人工抽样校验 |
| 消歧准确率 | >90% | 误分类率统计 |
| 创建知识结构耗时 | < 2 分钟 | 操作计时 |
| 跨领域知识关联发现 | 自动发现 | 簇间关联数量 |
| 图谱视图渲染时间 | < 2 秒 | 性能监控 |

---

## 11. 废弃项的后端清理清单

完成迁移后，以下代码和文件需要移除：

| 类别 | 具体项 |
|------|--------|
| Models | `Pyramid` class, `PyramidNode` 中的 `pyramid_id`/`parent_id`/`level`/`path`/`sort_order` |
| Routers | `pyramids.py` 中金字塔 CRUD 相关路由 |
| Services | 金字塔创建/更新/删除服务 |
| Schemas | 金字塔相关的 Pydantic schema |
| Features | `docs/features/core/pyramid-evolution/` 整个目录（被本文档替代） |
| 前端 | 所有金字塔视图页面和组件 |

---

## Metadata

- 规模: 大（架构级重构）
- 涉及模块: 全部核心模块
- 涉及端: Backend, Frontend
- 创建时间: 2026-02-20
- 状态: 草稿
