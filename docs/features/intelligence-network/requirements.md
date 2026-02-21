# 情报网络：认知驱动的主动信息获取体系

> **版本**: v3.0
> **创建时间**: 2026-02-21
> **状态**: 草稿
> **前置依赖**: [下一代知识架构](../next-gen-knowledge-architecture/requirements.md)（知识图谱簇 + AI 认知模型）
> **性质**: 基于认知框架（第一环）构建的情报获取与评估体系（第二环）

## 1. 概述

### 1.1 定位

认知框架定义了"我们关心什么"（知识图谱簇 + AI 认知模型），情报网络解决"怎么持续获取"。

当前系统的信息获取是被动管道：人工配置信源 → 定时抓取 → 入库。情报网络要做的是将其升级为**主动认知闭环**：

```
认知框架（我关心什么）
    ↓ 驱动
情报网络（去哪找、找什么、找到的好不好、还缺什么）
    ↓ 反馈
认知框架进化（发现新概念、调整关注边界）
```

### 1.2 四大能力

| # | 能力 | 现状 | 目标 |
|---|------|------|------|
| 1 | 认知驱动的信源发现 | 关键词搜索 → 人工审批 | 认知模型生成多维搜索策略 → 持续发现 → 审批 |
| 2 | 情报缺口感知 | 无（不知道自己缺什么） | 自动分析覆盖度 → 识别缺口 → 生成补充任务 |
| 3 | 信源情报价值评估 | 技术健康度（能不能抓到） | 认知价值评估（抓到的有没有用） |
| 4 | 情报感知与洞察 | 文章列表（用户自己读、自己总结） | 实时信号检测 → 事件驱动洞察生成 → 认知时间线积累 → 分级推送 |

### 1.3 与现有能力的关系

| 现有能力 | 变化 |
|----------|------|
| 抓取引擎（Firecrawl + RSS） | **保留**，作为情报网络的执行层 |
| 信源发现（关键词 → DuckDuckGo） | **直接替换**为认知驱动发现（见下方迁移说明） |
| 嗅探策略（低频拟人） | **保留并升级**，抓取频率由频率决策器动态调整 |
| 扩展信源适配器（微信/B站/YouTube） | **保留**，作为情报网络的渠道层 |
| 内容清洗与摘要 | **保留**，不变 |
| 内容代谢 | **保留并整合**，代谢评分纳入情报缺口分析 |
| 发现可视化（SSE） | **保留并升级**，SSE 阶段重新映射（见下方） |

**信源发现迁移说明：**

现有信源发现流程（`source_discovery.py`）直接替换为认知驱动发现，不设并行期。原方案未在工程上产生实际价值，无需保留兼容。

**SSE 阶段映射（现有 → 新）：**

| 现有阶段 | 新阶段 | 变化 |
|----------|--------|------|
| EXTRACT（提取关键词） | STRATEGY_GENERATE（生成搜索策略） | 从关键词提取升级为认知模型驱动的多维策略生成 |
| SEARCH（DuckDuckGo 搜索） | MULTI_CHANNEL_SEARCH（多渠道搜索） | 从单一搜索引擎扩展为多渠道并行搜索 |
| FILTER（过滤去重） | COGNITIVE_VERIFY（认知验证） | 从 URL 去重升级为 embedding 相似度 + LLM 语义验证 |
| PROPOSAL（生成提案） | PROPOSAL（生成提案） | 不变，复用现有审批流 |

---

## 2. 能力一：认知驱动的信源发现

### 2.1 现状问题

当前信源发现流程：
1. 从金字塔节点提取关键词（纯字符串）
2. 用 DuckDuckGo 搜索
3. 过滤去重
4. 人工审批

问题：
- 搜索策略是扁平的关键词列表，没有语义理解
- 一次性发现，不会持续追踪
- 不知道应该从哪些维度去搜索
- 发现结果和节点的关联是弱关联（"与节点X相关"），没有认知层面的匹配

### 2.2 目标

认知模型驱动信源发现：每个节点/簇的 AI 认知模型自动生成多维度搜索策略，持续发现新信源，发现结果通过认知模型验证相关性。

### 2.3 用户故事

#### Story 1: 认知模型生成搜索策略

As a 系统, I want 基于节点的 AI 认知模型自动生成多维度搜索策略, So that 信源发现不再依赖简单关键词。

**Acceptance Criteria:**

- [ ] AC1: 多维度策略生成
  - **Given**: 节点 "MCP协议" 拥有完整的 AI 认知模型
  - **When**: 触发信源发现任务
  - **Then**: AI 基于认知模型生成搜索策略，包含多个维度：
    - 直接搜索：基于 core_identity 和 aliases（"Model Context Protocol", "MCP server"）
    - 关联搜索：基于 related_concepts（"Anthropic tool use", "Claude function calling"）
    - 生态搜索：基于 context_signals 组合（"MCP SDK", "MCP transport layer"）
    - 对比搜索：基于 disambiguation 和 related_concepts（"MCP vs Function Calling"）
    - 渠道搜索：针对特定平台（GitHub trending "mcp"、掘金标签 "MCP"）
  - 每个维度标注预期收益和优先级

- [ ] AC2: 策略随认知模型进化
  - **Given**: 节点认知模型更新（新增了 context_signal "transport layer"）
  - **When**: 下一次信源发现任务触发
  - **Then**:
    - 搜索策略自动包含新维度（"MCP transport layer implementation"）
    - 不需要人工调整搜索词

#### Story 2: 持续发现机制

As a 系统, I want 信源发现不是一次性的而是持续运行的, So that 新出现的高质量信源能被及时捕获。

**Acceptance Criteria:**

- [ ] AC1: 定期发现调度
  - **Given**: 系统中存在活跃的知识簇和节点
  - **When**: 到达发现调度周期（可配置，默认每周）
  - **Then**:
    - 系统自动为活跃节点执行信源发现
    - 每周发现预算：最多 N 个节点参与发现（N 可配置，默认 20）
    - 节点按缺口严重度排序，优先处理覆盖度最低的节点
    - 每个节点每次发现的候选信源上限 20 个
    - 发现结果进入审批队列

- [ ] AC2: 事件驱动发现
  - **Given**: 系统创建了新节点或新簇
  - **When**: 节点/簇创建完成
  - **Then**:
    - 自动触发该节点/簇的首次信源发现
    - 不等待定期调度

- [ ] AC3: 发现结果的认知验证（embedding 优先）
  - **Given**: 搜索引擎返回了一批候选信源
  - **When**: 进入过滤阶段
  - **Then**:
    - URL 去重（已有信源排除）
    - 轻量抓取候选信源的 title + meta description（不抓全文）
    - 对抓取文本做 embedding，与目标节点的 embedding 做余弦相似度：
      - 节点 embedding 来源：将认知模型的 `core_identity` + `definition` + `aliases` + `context_signals` 拼接为文本后生成 embedding，缓存在 `knowledge_nodes.embedding` 字段中（认知模型更新时重新生成）
      - 相似度 > 0.7 → 直接通过（高置信度相关）
      - 相似度 < 0.3 → 直接排除（明显不相关）
      - 相似度 0.3-0.7 → 进入 LLM 语义验证（抓取首页/最新文章，用认知模型做完整判断）
    - 预期：70% 的候选通过 embedding 即可判断，仅 30% 需要 LLM
    - 验证结果附带推理过程（embedding 得分或 LLM 推理链）

#### Story 3: 跨渠道信源发现

As a 系统, I want 在多个渠道同时发现信源, So that 不遗漏任何有价值的信息来源。

**Acceptance Criteria:**

- [ ] AC1: 多渠道搜索
  - **Given**: 搜索策略生成完毕
  - **When**: 执行发现任务
  - **Then**: 同时在以下渠道搜索：
    - 通用搜索引擎（DuckDuckGo / Serper）
    - GitHub（仓库、Awesome 列表、Discussions）
    - 技术社区（掘金、Medium、Dev.to）
    - RSS 聚合（通过 RSSHub 发现可订阅源）
    - 社交媒体（Twitter/X 技术账号）
  - 每个渠道的结果标注来源渠道

- [ ] AC2: 渠道适配
  - **Given**: 不同渠道有不同的搜索方式
  - **When**: 执行搜索
  - **Then**:
    - 通用搜索引擎：使用自然语言查询
    - GitHub：使用 API 搜索仓库和话题
    - 技术社区：使用平台标签/分类搜索
    - 每个渠道有独立的适配器，遵循统一接口

### 2.4 搜索策略数据结构

```json
{
  "target_id": "uuid",
  "target_type": "node",
  "target_name": "MCP协议",
  "generated_at": "2026-02-21",
  "cognitive_model_version": 1,
  "dimensions": [
    {
      "type": "direct",
      "queries": ["Model Context Protocol", "MCP server development", "MCP 协议"],
      "channels": ["search_engine", "github"],
      "priority": "high",
      "expected_yield": "核心信源，直接讨论 MCP 的博客和仓库"
    },
    {
      "type": "ecosystem",
      "queries": ["MCP SDK python", "MCP transport SSE", "MCP client library"],
      "channels": ["github", "tech_community"],
      "priority": "medium",
      "expected_yield": "生态工具和实现，技术深度较高"
    },
    {
      "type": "related",
      "queries": ["Anthropic tool use blog", "Claude function calling tutorial"],
      "channels": ["search_engine"],
      "priority": "low",
      "expected_yield": "关联概念的信源，可能间接覆盖 MCP"
    },
    {
      "type": "comparative",
      "queries": ["MCP vs OpenAI function calling", "MCP alternatives"],
      "channels": ["search_engine", "tech_community"],
      "priority": "low",
      "expected_yield": "对比分析类内容，帮助理解 MCP 的定位"
    }
  ]
}
```

---

## 3. 能力二：情报缺口感知

### 3.1 现状问题

当前系统不知道自己"缺什么"：
- 一个节点有 50 篇内容和 0 篇内容，抓取行为完全一样
- 信源发现是无差别的，不会优先补充空白领域
- 没有"覆盖度"的概念，无法回答"我对 MCP 的了解够不够全面"

### 3.2 目标

系统能自动感知每个节点和簇的情报覆盖状况，识别缺口，并生成针对性的补充任务。

### 3.3 覆盖度模型

每个节点的情报覆盖度由以下维度综合评估：

```
覆盖度 = f(内容数量, 内容时效性, 内容多样性, 信源覆盖, 概念覆盖)
```

| 维度 | 计算方式 | 默认权重 |
|------|----------|----------|
| 内容数量 | 关联内容总数，对数衰减（10篇和100篇差距不大） | 20% |
| 内容时效性 | 最近 7/30/90 天的新增内容比例 | 25% |
| 内容多样性 | 内容来源的信源数量（避免单一信源依赖） | 20% |
| 信源覆盖 | 关联的活跃信源数量 | 15% |
| 概念覆盖 | 认知模型中的 context_signals 被内容覆盖的比例（见下方说明） | 20% |

**权重自适应机制：**

上述权重是默认值，不同领域特征的节点/簇应使用不同权重。系统支持两种调整方式：

1. AI 自动调整：根据节点的领域特征自动推荐权重配置
   - 快速变化领域（如 AI 新闻）：时效性权重提高到 40%，内容数量降低到 10%
   - 成熟稳定领域（如 TCP/IP 协议）：内容数量和多样性权重提高，时效性降低到 10%
   - 小众领域（如某个特定框架）：信源覆盖权重降低（本身信源就少），概念覆盖权重提高

2. 管理员手动覆盖：在簇或节点级别手动设置权重

权重配置存储在 `knowledge_clusters.metadata` 或 `knowledge_nodes.ai_model` 的 `coverage_weights` 字段中。

**概念覆盖维度的精度说明：**

概念覆盖需要判断"这篇内容覆盖了 context_signals 中的哪些信号"。执行方式：
- 使用关键词/短语匹配（context_signals 本身就是关键词列表），不调用 LLM
- 这是粗粒度的判断（信号词是否出现在文章中），不是精确的语义理解
- 精度不够时的降级：如果某个 signal 是复合概念（如 "transport layer security"），拆分为多个子信号词匹配
- 如果概念覆盖维度的计算结果持续不可靠（误报率 > 30%），可将其权重降为 0 暂时禁用

### 3.4 用户故事

#### Story 4: 节点级覆盖度分析

As a 系统, I want 自动计算每个节点的情报覆盖度, So that 识别哪些节点的信息获取不足。

**计算策略：增量更新 + 定期全量校准 + 手动重算**

- 增量更新（事件驱动）：当节点有新内容入库或信源变更时，仅重算该节点的覆盖度
- 全量校准（每周）：全量重算所有节点和簇的覆盖度，校准增量计算的累积误差
- 手动重算：管理员可随时触发单个节点/簇或全局的覆盖度重算
- 概念覆盖维度的匹配结果缓存在 `content_node_relations.matched_signals`（JSONB）中，新内容入库时计算一次，后续直接聚合

**Acceptance Criteria:**

- [ ] AC1: 覆盖度计算
  - **Given**: 节点 "MCP协议" 有 48 篇内容、5 个信源
  - **When**: 节点有新内容入库（增量更新）或每周全量校准触发
  - **Then**:
    - 计算各维度得分：
      - 内容数量: 0.85（48篇，充足）
      - 内容时效性: 0.90（最新内容 2 天前）
      - 内容多样性: 0.70（5 个信源，但 3 个是同一类型）
      - 信源覆盖: 0.60（缺少 GitHub 和社区类信源）
      - 概念覆盖: 0.75（context_signals 中 "transport layer" 相关内容为 0）
    - 综合覆盖度: 0.77
    - 生成覆盖度报告，标注薄弱维度

- [ ] AC2: 缺口识别
  - **Given**: 覆盖度分析完成
  - **When**: 某维度得分低于阈值（可配置，默认 0.5）
  - **Then**:
    - 生成具体的缺口描述：
      - "信源类型单一：5 个信源中 4 个是博客，缺少 GitHub 仓库和技术社区"
      - "概念盲区：认知模型中的 'transport layer' 相关内容为 0"
    - 缺口关联到具体的认知模型字段

#### Story 5: 簇级覆盖度全景

As a 知识管理员, I want 看到整个知识簇的情报覆盖全景, So that 快速定位最需要补充的领域。

**Acceptance Criteria:**

- [ ] AC1: 簇覆盖度热力图
  - **Given**: 簇 "AI 工具链" 包含 8 个节点
  - **When**: 查看簇的覆盖度分析
  - **Then**:
    - 展示所有成员节点的覆盖度排名：
      - MCP协议: 0.77 ✅
      - Function Calling: 0.52 ⚠️
      - LangChain: 0.25 🔴
      - CrewAI: 0.00 ❌
    - 簇整体覆盖度: 各节点加权平均
    - 高亮最薄弱的节点

- [ ] AC2: 跨簇对比
  - **Given**: 系统中有多个簇
  - **When**: 查看全局覆盖度
  - **Then**:
    - 展示所有簇的覆盖度排名
    - 标注哪些簇整体偏弱

#### Story 6: 自动生成情报补充任务

As a 系统, I want 基于缺口分析自动生成补充任务, So that 情报获取资源向最需要的地方倾斜。

**Acceptance Criteria:**

- [ ] AC1: 缺口驱动的信源发现
  - **Given**: 节点 "CrewAI" 覆盖度为 0（空白）
  - **When**: 缺口分析完成
  - **Then**:
    - 自动触发该节点的信源发现任务（优先级最高）
    - 搜索策略覆盖所有维度（直接 + 生态 + 关联 + 渠道）
    - 生成 `DISCOVER_SOURCES` 类型的任务，进入任务队列

- [ ] AC2: 缺口驱动的抓取频率调整
  - **Given**: 节点 "Function Calling" 时效性得分低（最新内容 15 天前）
  - **When**: 缺口分析完成
  - **Then**:
    - 生成 `ADJUST_CRAWL_FREQUENCY` 类型的建议
    - 建议进入频率决策器（见下方仲裁规则），不直接生效
    - 管理员审批后执行（或配置为自动执行低风险调整）

**频率决策仲裁规则：**

缺口感知（能力二）和价值评估（能力三）都会产生频率调整建议，可能冲突。所有频率建议汇总到频率决策器，按以下规则仲裁：

1. 价值评估的降频优先级高于缺口感知的提频（宁可慢一点，也不浪费资源抓垃圾）
2. 缺口驱动的提频只作用于该节点下情报价值 > 0.4 的信源（不给低价值信源提频）
3. 如果节点所有信源价值都 < 0.4，缺口感知不提频，而是触发信源发现（找新的替代信源）
4. 最终频率受上下限保护：最高不超过 30 分钟/次，最低不低于 7 天/次

- [ ] AC3: 缺口驱动的概念补充
  - **Given**: 节点 "MCP协议" 的概念覆盖中 "transport layer" 为空白
  - **When**: 缺口分析完成
  - **Then**:
    - 生成针对性搜索任务：专门搜索 "MCP transport layer" 相关信源
    - 如果持续无法找到内容，建议将 "MCP Transport" 拆分为独立节点

### 3.5 覆盖度报告数据结构

```json
{
  "node_id": "uuid",
  "node_name": "MCP协议",
  "analyzed_at": "2026-02-21",
  "overall_coverage": 0.77,
  "dimensions": {
    "content_volume": {
      "score": 0.85,
      "detail": {"total": 48, "threshold_for_full": 20}
    },
    "content_freshness": {
      "score": 0.90,
      "detail": {"last_7d": 12, "last_30d": 35, "latest_at": "2026-02-19"}
    },
    "content_diversity": {
      "score": 0.70,
      "detail": {"source_count": 5, "type_distribution": {"blog": 3, "news": 1, "rss": 1}}
    },
    "source_coverage": {
      "score": 0.60,
      "detail": {"active_sources": 5, "missing_channels": ["github", "tech_community"]}
    },
    "concept_coverage": {
      "score": 0.75,
      "detail": {
        "covered_signals": ["protocol", "server", "client", "tool use"],
        "uncovered_signals": ["transport layer", "SSE transport"]
      }
    }
  },
  "gaps": [
    {
      "type": "source_type_gap",
      "severity": "medium",
      "description": "缺少 GitHub 仓库和技术社区类信源",
      "suggested_action": "DISCOVER_SOURCES",
      "action_params": {"channels": ["github", "tech_community"]}
    },
    {
      "type": "concept_blind_spot",
      "severity": "high",
      "description": "认知模型中 'transport layer' 相关内容为 0",
      "suggested_action": "TARGETED_DISCOVERY",
      "action_params": {"queries": ["MCP transport layer", "MCP SSE implementation"]}
    }
  ]
}
```

---

## 4. 能力三：信源情报价值评估

### 4.1 现状问题

当前信源只有技术层面的 `health_score`（能不能抓到），没有认知层面的评估（抓到的有没有用）：
- 一个信源每次都能抓成功（health_score = 100），但抓到的内容全是广告或无关信息
- 一个信源产出大量内容，但全是重复信息，没有新洞察
- 无法回答"这个信源对我的知识体系有多大贡献"

### 4.2 目标

建立信源的情报价值评估体系，从"能不能抓到"升级为"抓到的值不值"，并用评估结果反向驱动抓取策略。

### 4.3 情报价值模型

每个信源的情报价值由以下维度综合评估：

```
情报价值 = f(内容命中率, 认知贡献度, 时效性, 独占性, 稳定性)
```

| 维度 | 定义 | 计算方式 |
|------|------|----------|
| 内容命中率 | 抓到的内容中，被分类到节点的比例 | 已分类内容数 / 总抓取内容数 |
| 认知贡献度 | 命中的内容是否带来了新信息 | 非重复内容比例 × 概念新颖度（见下方说明） |
| 时效性 | 内容从发布到被抓取的延迟 | 平均延迟时间的倒数 |
| 独占性 | 该信源提供的内容是否在其他信源中也能获取 | 基于 content_hash 精确去重（见下方说明） |
| 稳定性 | 信源的持续产出能力 | 过去 30 天的产出频率和成功率 |

**认知贡献度中"概念新颖度"的定义：**

概念新颖度通过 embedding 距离衡量，不依赖关键词匹配：
- 新内容入库时已有 embedding（内容处理流程生成）
- 该节点已有内容也都有 embedding
- 新颖度 = 新内容 embedding 与该节点已有内容 embedding 集合的最小余弦距离
  - 距离大（> 0.5）→ 高新颖度（讨论了该节点下前所未有的角度）
  - 距离小（< 0.2）→ 低新颖度（和已有内容高度相似）
- 认知贡献度 = 非重复内容比例 × 平均新颖度
- 成本：embedding 已是现成数据，只需向量距离计算，零额外 LLM 调用

**新颖度计算的性能策略：**

当节点内容量较大时（如 500 篇），逐一计算余弦距离的成本会累积。采用以下策略：
- 使用 pgvector 的近似最近邻（ANN）索引加速查询，单次查询 < 5ms
- 信源价值评估时批量计算：一次性查询该信源所有内容的最近邻距离，避免逐条查询
- 新颖度得分在内容入库时计算一次并缓存（存储在 `content_node_relations.novelty_score`），评估时直接聚合

**独占性计算的精度与成本取舍：**

独占性判断"这篇内容是否在其他信源中也能获取"，有两种精度：
- 精确去重（content_hash）：同一篇文章被多个信源转载，hash 完全一致。成本低，O(1) 查询。
- 语义去重（"同一事件的不同报道"）：不同文章讨论同一件事。需要语义比对，成本高。

**本方案采用精确去重**，理由：
1. 成本可控：只需查询 content_hash 索引
2. 对于 RSS/博客类信源，转载和聚合是主要的重复来源，精确去重已能覆盖大部分场景
3. 语义去重可作为后续优化，在积累足够数据后再评估是否值得引入

### 4.4 用户故事

#### Story 7: 信源情报价值计算

As a 系统, I want 自动计算每个信源的情报价值, So that 区分高价值信源和低价值信源。

**Acceptance Criteria:**

- [ ] AC1: 定期评估
  - **Given**: 信源 "某技术博客" 已运行 30 天，抓取了 100 篇内容
  - **When**: 执行情报价值评估（每周定时）
  - **Then**:
    - 计算各维度得分：
      - 内容命中率: 0.30（100 篇中 30 篇被分类到节点）
      - 认知贡献度: 0.20（30 篇命中内容中，25 篇与已有内容高度重复）
      - 时效性: 0.80（平均发布后 3 小时被抓取）
      - 独占性: 0.10（大部分内容在其他信源也能获取）
      - 稳定性: 0.90（持续产出，抓取成功率高）
    - 综合情报价值: 0.35
    - 生成评估报告

- [ ] AC2: 按节点维度的价值分解
  - **Given**: 信源关联了 3 个节点
  - **When**: 评估完成
  - **Then**:
    - 分别计算该信源对每个节点的贡献：
      - 对 "MCP协议": 价值 0.60（命中率高，内容相关）
      - 对 "LangChain": 价值 0.10（偶尔提到，不是主要内容）
      - 对 "CrewAI": 价值 0.00（从未命中）
    - 建议调整信源-节点关联权重

#### Story 8: 价值驱动的抓取策略

As a 系统, I want 根据信源情报价值自动调整抓取策略, So that 资源向高价值信源倾斜。

**Acceptance Criteria:**

- [ ] AC1: 高价值信源优待
  - **Given**: 信源 A 情报价值 0.85，信源 B 情报价值 0.20
  - **When**: 调度器分配抓取任务
  - **Then**:
    - 频率建议进入频率决策器（见 Story 6 AC2 仲裁规则）
    - 信源 A：提高抓取频率（如从 4 小时降到 1 小时）
    - 信源 B：降低抓取频率（如从 4 小时升到 12 小时）
    - 频率调整有上下限保护（最高 30 分钟/次，最低 7 天/次）

- [ ] AC2: 低价值信源处置建议
  - **Given**: 信源连续 4 周情报价值 < 0.2
  - **When**: 评估完成
  - **Then**:
    - 生成 `DEACTIVATE_SOURCE` 建议
    - 建议包含：低价值原因分析、替代信源推荐（如果有）
    - 管理员审批后停用

- [ ] AC3: 信源替换建议
  - **Given**: 某节点的所有信源情报价值都偏低
  - **When**: 评估完成
  - **Then**:
    - 触发该节点的信源发现任务，寻找替代信源
    - 生成 `REPLACE_SOURCE` 建议，包含新旧信源对比

#### Story 9: 信源情报价值仪表盘

As a 知识管理员, I want 在仪表盘上看到所有信源的情报价值排名, So that 快速了解信源质量全貌。

**Acceptance Criteria:**

- [ ] AC1: 信源价值排行
  - **Given**: 系统中有 50 个活跃信源
  - **When**: 查看信源仪表盘
  - **Then**:
    - 按情报价值降序排列
    - 颜色标注：绿色（>0.7）、黄色（0.4-0.7）、红色（<0.4）
    - 显示各维度的雷达图

- [ ] AC2: 价值趋势
  - **Given**: 信源已运行多周
  - **When**: 查看信源详情
  - **Then**:
    - 展示情报价值的周趋势折线图
    - 标注价值突变点（如某周突然下降）及可能原因

### 4.5 信源情报价值数据结构

```json
{
  "source_id": "uuid",
  "source_name": "某技术博客",
  "evaluated_at": "2026-02-21",
  "period": "last_30_days",
  "overall_value": 0.35,
  "dimensions": {
    "hit_rate": {
      "score": 0.30,
      "detail": {"total_crawled": 100, "classified": 30, "unclassified": 70}
    },
    "cognitive_contribution": {
      "score": 0.20,
      "detail": {"unique_insights": 5, "duplicates": 25, "novelty_ratio": 0.17, "avg_embedding_distance": 0.23}
    },
    "timeliness": {
      "score": 0.80,
      "detail": {"avg_delay_hours": 3.2, "max_delay_hours": 12}
    },
    "exclusivity": {
      "score": 0.10,
      "detail": {"exclusive_contents": 3, "total_classified": 30}
    },
    "stability": {
      "score": 0.90,
      "detail": {"success_rate": 0.98, "output_frequency": "2.3/day"}
    }
  },
  "node_breakdown": [
    {"node_id": "uuid", "node_name": "MCP协议", "value": 0.60},
    {"node_id": "uuid", "node_name": "LangChain", "value": 0.10},
    {"node_id": "uuid", "node_name": "CrewAI", "value": 0.00}
  ],
  "recommendations": [
    {
      "type": "REDUCE_FREQUENCY",
      "reason": "综合情报价值偏低（0.35），认知贡献度极低（0.20）",
      "suggested_interval": 43200
    }
  ]
}
```

---

## 5. 能力四：情报感知与洞察

### 5.1 现状问题

当前系统的内容消费模式是"素材罗列"：
- 用户看到的是按时间排序的文章列表
- 每篇文章有标题、摘要、来源，但没有跨文章的综合分析
- 用户需要自己阅读、自己总结、自己判断趋势
- 无法回答"这个领域最近发生了什么"这种高层问题

本质问题：系统交付的是"检索结果"而非"情报"。简报模式（定期生成周报）只是把"文章列表"换了个皮，本质上仍然是被动的、按日历切片的信息罗列。

### 5.2 目标

系统是一个**持续运转的情报分析师**，不是一个定时报告生成器。它的工作方式是：

1. **持续消化**：每篇内容入库时就在更新对领域的认知，不是攒一周再看
2. **产出洞察**：交付的是"发生了什么、意味着什么、你应该关注什么"，不是"本周有 N 篇文章"
3. **事件驱动**：有值得说的才说，没有就不说。不按日历推送，按信号推送
4. **持续积累**：洞察不是一次性的，而是在节点上持续积累形成认知记忆

核心区别：

| 维度 | 简报模式（废弃） | 情报感知模式（目标） |
|------|-----------------|---------------------|
| 触发 | 按日历（每周一次） | 按信号（有洞察才产出） |
| 粒度 | 固定时间窗口切片 | 单条洞察，可聚合 |
| 内容 | 摘要拼接 + 趋势总结 | 事件识别 + 影响分析 + 概念演变追踪 |
| 积累 | 每期独立，无记忆 | 洞察持续积累在节点上，形成认知时间线 |
| 交互 | 被动阅读 | 可追问、可溯源、可反馈 |

### 5.3 情报感知的三层架构

```
第一层：信号检测（实时，内容入库时触发）
├── 新概念涌现：节点下首次出现的高频词/短语
├── 内容突增：短时间内某节点内容量异常增长
├── 情绪/立场转变：同一话题的讨论基调发生变化
├── 跨节点共振：多个节点同时出现相关内容
└── 产出：intelligence_signals（原始信号，轻量级，不调用 LLM）

第二层：洞察生成（信号驱动，有信号才触发）
├── 将一个或多个相关信号 + 关联的原始内容送入 LLM
├── LLM 作为分析师：这些信号意味着什么？对该领域有什么影响？
├── 产出：intelligence_insights（结构化洞察，带溯源和置信度）
└── 洞察挂载到节点/簇上，形成认知时间线

第三层：洞察推送（洞察生成后触发）
├── 按用户订阅的节点/簇过滤
├── 按洞察的重要性分级推送（重大 → 即时推送，一般 → 汇总推送）
└── 用户可对洞察反馈（认同/不认同/追问）
```

### 5.4 信号检测机制

信号是情报感知的原始输入，轻量级、实时、不调用 LLM。

#### 5.4.1 信号类型

| 信号类型 | 检测时机 | 检测方式 | 示例 |
|----------|----------|----------|------|
| `CONCEPT_EMERGENCE` | 内容入库时 | 新内容中出现节点 context_signals 之外的高频词（3 篇以上提及且此前未见） | "MCP Gateway" 一词在 3 天内出现 4 次 |
| `CONTENT_SURGE` | 内容入库时 | 节点 24h 内新增内容数 > 日均值 × 3（日均值 = 过去 30 天均值，新节点用全局中位数兜底） | MCP 节点日均 2 篇，今天已入库 8 篇 |
| `CROSS_NODE_RESONANCE` | 内容分类时 | 同一篇内容被分类到 2+ 个节点，或 24h 内多个节点出现语义相似的内容（embedding 相似度 > 0.8） | "MCP + LangChain 集成" 同时命中两个节点 |
| `NOVELTY_SPIKE` | 内容入库时 | 新内容的新颖度得分（embedding 距离）显著高于该节点近期均值（> 均值 + 2σ） | 一篇讨论 "MCP over WebSocket" 的文章，与已有内容差异极大 |
| `SOURCE_PATTERN_SHIFT` | 内容入库时 | 某信源的内容主题分布发生显著变化（近 7 天 vs 前 30 天的节点命中分布差异 > 阈值） | 某博客从主要讨论 LangChain 转向大量讨论 MCP |

#### 5.4.2 信号数据结构

```json
{
  "id": "uuid",
  "signal_type": "CONCEPT_EMERGENCE",
  "target_id": "uuid",
  "target_type": "node",
  "detected_at": "2026-02-21T14:30:00Z",
  "severity": "medium",
  "data": {
    "term": "MCP Gateway",
    "mention_count": 4,
    "first_seen": "2026-02-18",
    "content_ids": ["uuid-1", "uuid-2", "uuid-3", "uuid-4"]
  },
  "processed": false
}
```

#### 5.4.3 信号严重度判定

| 严重度 | 条件 | 推送策略 |
|--------|------|----------|
| `critical` | CONTENT_SURGE（> 日均 5 倍）或 CROSS_NODE_RESONANCE（涉及 3+ 节点） | 即时推送 |
| `high` | CONCEPT_EMERGENCE（5+ 篇提及）或 NOVELTY_SPIKE | 1 小时内推送 |
| `medium` | CONTENT_SURGE（3-5 倍）或 CONCEPT_EMERGENCE（3-4 篇） | 汇入每日摘要 |
| `low` | SOURCE_PATTERN_SHIFT 或其他弱信号 | 仅记录，不主动推送 |

### 5.5 用户故事

#### Story 10: 实时信号检测

As a 系统, I want 在内容入库时实时检测情报信号, So that 不遗漏任何值得关注的变化。

**Acceptance Criteria:**

- [ ] AC1: 内容入库触发信号检测
  - **Given**: 一篇新内容被分类到节点 "MCP协议"
  - **When**: 内容入库完成
  - **Then**:
    - 检查是否触发 CONCEPT_EMERGENCE（扫描新词频）
    - 检查是否触发 CONTENT_SURGE（对比日均值）
    - 检查是否触发 CROSS_NODE_RESONANCE（检查多节点命中）
    - 检查是否触发 NOVELTY_SPIKE（对比新颖度均值）
    - 所有检测均为本地计算（词频统计 + embedding 距离 + 计数），不调用 LLM
    - 检测到的信号写入 `intelligence_signals` 表

- [ ] AC2: 信号去重与合并
  - **Given**: 同一个新概念 "MCP Gateway" 在 3 篇内容中被检测到
  - **When**: 第 2、3 次检测到相同信号
  - **Then**:
    - 不重复创建信号，而是更新已有信号的 mention_count 和 content_ids
    - 信号合并窗口：同类型 + 同目标 + 同关键数据，72 小时内合并

#### Story 11: 信号驱动的洞察生成

As a 系统, I want 基于检测到的信号自动生成情报洞察, So that 用户收到的是分析结论而非原始数据。

**Acceptance Criteria:**

- [ ] AC1: 单信号洞察
  - **Given**: 检测到 CONCEPT_EMERGENCE 信号（"MCP Gateway" 出现 4 次）
  - **When**: 信号严重度 >= medium 且未被处理
  - **Then**:
    - 收集信号关联的所有原始内容摘要
    - 将内容摘要 + 节点认知模型 + 信号描述送入 LLM
    - LLM 分析：这个新概念是什么？为什么突然出现？对该领域意味着什么？
    - 产出结构化洞察：
      ```
      【MCP协议 · 新概念涌现】
      "MCP Gateway" 概念在 3 天内被 4 篇文章提及，此前未见。
      分析：MCP Gateway 是一种中间层代理，用于在多个 MCP Server 之间做路由和鉴权。
      这表明 MCP 生态正从"单 Server 对接"向"多 Server 编排"演进。
      影响：如果你在追踪 MCP 的架构演进，这是一个值得关注的方向。
      溯源：[文章1] [文章2] [文章3] [文章4]
      ```
    - 洞察挂载到节点 "MCP协议" 的认知时间线上

- [ ] AC2: 多信号关联洞察
  - **Given**: 同一节点在 24h 内产生了 CONTENT_SURGE + CONCEPT_EMERGENCE 两个信号
  - **When**: 洞察生成器检测到信号聚集
  - **Then**:
    - 将多个信号合并分析（而非分别生成独立洞察）
    - LLM 从更高视角分析：为什么同时出现内容突增和新概念？是否有重大事件发生？
    - 产出综合洞察，严重度取信号中的最高值

- [ ] AC3: 跨节点洞察
  - **Given**: CROSS_NODE_RESONANCE 信号涉及 "MCP协议" 和 "AI 安全" 两个节点
  - **When**: 生成洞察
  - **Then**:
    - 洞察同时挂载到两个节点
    - 分析跨领域关联的含义（如 "MCP 安全模型开始受到关注，工具链和安全两个领域出现交叉"）
    - 如果两个节点属于不同簇，标注为跨簇洞察

- [ ] AC4: 洞察质量保障
  - **Given**: LLM 生成了洞察
  - **When**: 洞察进入存储流程
  - **Then**:
    - 洞察中的每个事实性陈述必须关联到具体的 content_id（可溯源）
    - 洞察的置信度由信号强度和内容数量决定（不是 LLM 自评）
    - 置信度计算：信号严重度权重 × 关联内容数量的对数 × 内容来源多样性

#### Story 12: 认知时间线

As a 知识管理员, I want 看到每个节点的情报洞察时间线, So that 理解一个领域的演变脉络。

**Acceptance Criteria:**

- [ ] AC1: 节点认知时间线
  - **Given**: 节点 "MCP协议" 在过去一个月积累了 8 条洞察
  - **When**: 查看节点详情
  - **Then**:
    - 按时间倒序展示洞察列表
    - 每条洞察显示：类型标签、摘要、时间、关联内容数、置信度
    - 可展开查看完整分析和溯源内容
    - 可按洞察类型筛选（新概念、内容突增、跨节点关联等）

- [ ] AC2: 簇级洞察聚合
  - **Given**: 簇 "AI 工具链" 下的多个节点都有洞察
  - **When**: 查看簇详情
  - **Then**:
    - 聚合展示簇下所有节点的洞察，按时间排序
    - 高亮跨节点洞察（涉及簇内多个节点的）
    - 展示簇级态势摘要（由最近 N 条高严重度洞察自动聚合，可选触发 LLM 生成簇级综合分析）

- [ ] AC3: 用户可追问
  - **Given**: 用户看到一条洞察 "MCP Gateway 概念涌现"
  - **When**: 用户点击"追问"
  - **Then**:
    - 进入对话模式，上下文包含：该洞察 + 关联的原始内容 + 节点认知模型
    - 用户可以问："MCP Gateway 和现有的 API Gateway 有什么区别？"
    - LLM 基于已有内容回答，如果内容不足以回答，明确告知"当前素材不足以判断"

#### Story 13: 洞察订阅与推送

As a 知识管理员, I want 订阅感兴趣的节点/簇的情报洞察, So that 重要变化能及时通知我。

**Acceptance Criteria:**

- [ ] AC1: 订阅管理
  - **Given**: 用户对 "MCP协议" 节点感兴趣
  - **When**: 设置订阅
  - **Then**:
    - 可选择推送阈值（仅 critical / high 以上 / 全部）
    - 可选择接收方式（站内通知 / 邮件）
    - 可同时订阅多个节点和簇

- [ ] AC2: 分级推送
  - **Given**: 洞察生成完成
  - **When**: 推送给订阅用户
  - **Then**:
    - critical 洞察：即时推送
    - high 洞察：1 小时内推送
    - medium 洞察：汇入每日摘要（每天一次，汇总当天所有 medium 洞察）
    - low 洞察：不主动推送，用户在时间线中自行查看
    - 每日摘要不是"简报"，而是洞察条目的列表，每条一句话摘要 + 链接

- [ ] AC3: 洞察反馈
  - **Given**: 用户收到一条洞察推送
  - **When**: 用户阅读后
  - **Then**:
    - 可标记"有价值"或"噪音"
    - "噪音"反馈会降低同类信号的严重度权重（自适应）
    - "有价值"反馈产出 `INSIGHT_FEEDBACK` 进化信号（供认知框架消费）

### 5.6 洞察数据结构

```json
{
  "id": "uuid",
  "target_id": "uuid",
  "target_type": "node",
  "target_name": "MCP协议",
  "insight_type": "concept_emergence",
  "severity": "high",
  "confidence": 0.82,
  "generated_at": "2026-02-21T15:00:00Z",
  "title": "新概念涌现：MCP Gateway",
  "summary": "MCP Gateway 概念在 3 天内被 4 篇文章提及，表明 MCP 生态正从单 Server 向多 Server 编排演进。",
  "analysis": "MCP Gateway 是一种中间层代理，用于在多个 MCP Server 之间做路由和鉴权。这一概念的出现意味着...",
  "impact": "如果你在追踪 MCP 的架构演进，多 Server 编排是一个值得关注的新方向。",
  "signal_ids": ["uuid-signal-1"],
  "source_content_ids": ["uuid-1", "uuid-2", "uuid-3", "uuid-4"],
  "source_content_count": 4,
  "related_node_ids": [],
  "feedback_stats": {
    "valuable": 0,
    "noise": 0
  }
}

---

## 6. 四大能力的协同闭环

```
┌──────────────────────────────────────────────────────────────────────┐
│                        情报网络运行闭环                               │
│                                                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │ 认知驱动发现 │ ──→ │ 抓取与处理   │ ──→ │ 内容分类入库 │           │
│  │ (能力一)     │     │ (现有引擎)   │     │ (认知模型)   │           │
│  └──────┬──────┘     └─────────────┘     └──────┬──────┘           │
│         │                                        │                   │
│         │         ┌──────────────────┐           │                   │
│         │         │                  │           │                   │
│         ▼         ▼                  │           ▼                   │
│  ┌─────────────────────┐    ┌───────┴───────────────┐              │
│  │ 情报缺口感知 (能力二) │    │ 信源价值评估 (能力三)  │              │
│  │                     │    │                       │              │
│  │ - 覆盖度分析        │    │ - 命中率/贡献度/独占性 │              │
│  │ - 缺口识别          │    │ - 抓取频率调整         │              │
│  │ - 补充任务生成      │    │ - 低价值信源处置       │              │
│  └──────┬──────────────┘    └───────┬───────────────┘              │
│         │                           │                               │
│         │     ┌─────────────┐       │                               │
│         └───→ │ 反馈到能力一 │ ←─────┘                               │
│               │             │                                       │
│               │ - 缺口驱动发现优先级                                  │
│               │ - 价值评估优化搜索策略                                 │
│               │ - 产出进化信号（供认知框架消费）                        │
│               └─────────────┘                                       │
│                                                                      │
│         ┌──────────────────────────────────────┐                    │
│         │ 情报感知与洞察 (能力四) ← 内容分类入库  │                    │
│         │                                      │                    │
│         │ - 实时信号检测（新概念/突增/跨节点共振）│                    │
│         │ - 信号驱动洞察生成（LLM 分析）         │                    │
│         │ - 认知时间线积累                       │                    │
│         │ - 用户反馈 → 认知模型进化信号          │                    │
│         └──────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
```

### 闭环运行示例

以节点 "CrewAI" 为例，完整的情报网络闭环：

```
1. 缺口感知：CrewAI 覆盖度 = 0，标记为"空白"
       ↓
2. 认知驱动发现：基于 CrewAI 的认知模型生成搜索策略
   - 直接搜索: "CrewAI framework", "CrewAI multi-agent"
   - 生态搜索: "CrewAI examples", "CrewAI vs AutoGen"
   - 渠道搜索: GitHub "crewai", 掘金标签 "CrewAI"
       ↓
3. 发现结果：找到 8 个候选信源
   - 认知验证：5 个通过（确实在讨论 CrewAI），3 个排除
   - 进入审批队列
       ↓
4. 管理员审批：通过 4 个信源
       ↓
5. 抓取引擎：开始抓取，首批获取 15 篇内容
       ↓
6. 认知模型分类：12 篇分类到 CrewAI 节点，3 篇孤立
       ↓
7. 覆盖度更新：CrewAI 覆盖度从 0 升到 0.45
   - 仍有缺口：缺少 "CrewAI 与 LangChain 集成" 相关内容
       ↓
8. 信源价值评估：4 个新信源中
   - 2 个高价值（命中率 > 0.7）→ 提高抓取频率
   - 1 个中等（命中率 0.4）→ 保持
   - 1 个低价值（命中率 0.1）→ 降低频率
       ↓
9. 产出进化信号：从已分类内容中发现新的高频词 "crew orchestration"
   → 写入进化信号队列（供第一环认知框架消费）
   → 认知框架决定是否更新认知模型 → 搜索策略自动扩展
       ↓
10. 情报感知：内容入库过程中检测到信号
   → CONCEPT_EMERGENCE: "crew orchestration" 一词在 4 篇中出现（此前未见）
   → 信号触发洞察生成：LLM 分析后产出洞察 "CrewAI 社区开始讨论编排模式"
   → 洞察挂载到 CrewAI 节点的认知时间线
   → 推送给订阅了 CrewAI 的用户
   → 用户反馈"有价值" → 产出 INSIGHT_FEEDBACK 进化信号
       ↓
11. 下一轮循环...
```

### 与认知框架（第一环）的职责边界

情报网络（第二环）只负责产出进化信号，不负责认知模型的更新逻辑。

**情报网络产出的进化信号类型：**

| 信号类型 | 触发时机 | 数据内容 |
|----------|----------|----------|
| `NEW_HIGH_FREQ_TERM` | 内容分类后统计发现新高频词 | 节点 ID、新词、出现频次、来源内容 ID 列表 |
| `UNCOVERED_CONCEPT` | 覆盖度分析发现概念盲区 | 节点 ID、未覆盖的 context_signal、持续时长 |
| `DISAMBIGUATION_CASE` | 分类过程中遇到新的消歧案例 | 节点 ID、混淆概念、判断依据 |
| `CLUSTER_DRIFT` | 簇覆盖度分析发现成员节点关联模式变化 | 簇 ID、漂移节点、新关联方向 |
| `BRIEF_FEEDBACK` | 用户对洞察标记"有价值/噪音"反馈 | 洞察 ID、目标节点/簇 ID、反馈类型、洞察中的关键概念和分析结论（供认知框架判断哪些概念被用户认可或否定） |

**信号流向：**
```
情报网络 → evolution_signals 队列 → 认知框架消费 → 生成认知模型更新提案 → 审批
```

情报网络不关心认知框架如何处理这些信号，只保证信号的准确性和及时性。

---

## 7. 数据模型变更

### 7.1 新增表

```sql
-- 搜索策略（支持节点级和簇级）
CREATE TABLE discovery_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL,                    -- 节点 ID 或簇 ID
    target_type VARCHAR(20) NOT NULL,           -- node, cluster
    strategy JSONB NOT NULL,                    -- 多维度搜索策略（见 2.4 数据结构）
    cognitive_model_version INTEGER,            -- 生成时的认知模型版本
    status VARCHAR(20) DEFAULT 'active',        -- active, expired
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 覆盖度报告
CREATE TABLE coverage_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL,                    -- 节点 ID 或簇 ID
    target_type VARCHAR(20) NOT NULL,           -- node, cluster
    overall_coverage FLOAT NOT NULL,
    dimensions JSONB NOT NULL,                  -- 各维度得分详情（见 3.5 数据结构）
    gaps JSONB,                                 -- 识别到的缺口列表
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 信源情报价值评估
CREATE TABLE source_intelligence_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES information_sources(id) ON DELETE CASCADE,
    period VARCHAR(20) NOT NULL,                -- last_7_days, last_30_days
    overall_value FLOAT NOT NULL,
    dimensions JSONB NOT NULL,                  -- 各维度得分详情（见 4.5 数据结构）
    node_breakdown JSONB,                       -- 按节点的价值分解
    recommendations JSONB,                      -- 生成的建议
    evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 情报信号（实时检测，轻量级）
CREATE TABLE intelligence_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_type VARCHAR(50) NOT NULL,           -- CONCEPT_EMERGENCE, CONTENT_SURGE, CROSS_NODE_RESONANCE, NOVELTY_SPIKE, SOURCE_PATTERN_SHIFT
    target_id UUID NOT NULL,                    -- 节点 ID 或簇 ID
    target_type VARCHAR(20) NOT NULL,           -- node, cluster
    severity VARCHAR(20) NOT NULL,              -- critical, high, medium, low
    data JSONB NOT NULL,                        -- 信号详情（关键词、计数、content_ids 等）
    processed BOOLEAN DEFAULT FALSE,            -- 是否已被洞察生成器处理
    insight_id UUID,                            -- 关联的洞察 ID（处理后回填）
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    merged_count INTEGER DEFAULT 1              -- 合并次数（同类信号 72h 内合并）
);

-- 情报洞察（信号驱动生成，LLM 分析产出）
CREATE TABLE intelligence_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL,                    -- 主目标节点/簇 ID
    target_type VARCHAR(20) NOT NULL,           -- node, cluster
    insight_type VARCHAR(50) NOT NULL,          -- concept_emergence, content_surge, cross_node_resonance, novelty_spike, source_shift, composite
    severity VARCHAR(20) NOT NULL,              -- critical, high, medium, low
    confidence FLOAT NOT NULL,                  -- 置信度（由信号强度和内容数量计算）
    title VARCHAR(200) NOT NULL,                -- 洞察标题（一句话）
    summary TEXT NOT NULL,                      -- 洞察摘要
    analysis TEXT NOT NULL,                     -- 完整分析（LLM 产出）
    impact TEXT,                                -- 影响分析
    signal_ids UUID[] NOT NULL,                 -- 触发该洞察的信号 ID 列表
    source_content_ids UUID[] NOT NULL,         -- 溯源内容 ID 列表
    source_content_count INTEGER NOT NULL,
    related_node_ids UUID[],                    -- 跨节点洞察时的关联节点
    feedback_stats JSONB DEFAULT '{"valuable": 0, "noise": 0}',
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 洞察订阅
CREATE TABLE insight_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,                      -- 订阅用户
    target_id UUID NOT NULL,                    -- 订阅的节点 ID 或簇 ID
    target_type VARCHAR(20) NOT NULL,           -- node, cluster
    min_severity VARCHAR(20) NOT NULL DEFAULT 'medium',  -- 推送阈值：critical, high, medium, low
    delivery_method VARCHAR(20) NOT NULL DEFAULT 'in_app',  -- in_app, email
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, target_id, target_type)    -- 同一用户对同一目标不重复订阅
);

-- 情报任务：复用现有 change_proposals 表，不新增独立表
-- 新增以下 proposal type：
--   DISCOVER_SOURCES       (信源发现)
--   TARGETED_DISCOVERY     (针对性发现)
--   ADJUST_CRAWL_FREQUENCY (调整抓取频率)
--   DEACTIVATE_SOURCE      (停用信源)
--   REPLACE_SOURCE         (替换信源)
--
-- change_proposals.content JSONB 中存放任务参数（目标节点/信源、搜索策略等）
-- change_proposals.reason 中存放触发来源描述（coverage_gap / value_assessment / manual）
-- 审批流程与现有提案完全一致，管理员在同一个审批中心处理所有类型的提案
```

### 7.2 升级现有表

```sql
-- information_sources 新增字段
ALTER TABLE information_sources ADD COLUMN intelligence_value FLOAT DEFAULT 0.0;
ALTER TABLE information_sources ADD COLUMN last_evaluated_at TIMESTAMPTZ;
ALTER TABLE information_sources ADD COLUMN discovery_source VARCHAR(50);
    -- 发现来源: manual, cognitive_discovery, gap_driven, replacement

-- knowledge_nodes 新增字段
ALTER TABLE knowledge_nodes ADD COLUMN embedding VECTOR;
    -- 认知模型 embedding：由 core_identity + definition + aliases + context_signals 拼接生成
    -- 认知模型更新时自动重新生成，用于信源发现的认知验证

-- source_knowledge_relations 新增字段（信源-节点关联）
ALTER TABLE source_knowledge_relations ADD COLUMN contribution_value FLOAT DEFAULT 0.0;
    -- 该信源对该节点的情报贡献值
ALTER TABLE source_knowledge_relations ADD COLUMN last_evaluated_at TIMESTAMPTZ;

-- content_node_relations 新增字段（内容-节点关联）
ALTER TABLE content_node_relations ADD COLUMN matched_signals JSONB;
    -- 缓存概念覆盖匹配结果，如 ["protocol", "server", "tool use"]
    -- 新内容入库时计算一次，后续覆盖度分析直接聚合，避免重复匹配
ALTER TABLE content_node_relations ADD COLUMN novelty_score FLOAT;
    -- 缓存该内容相对于节点已有内容的新颖度得分（embedding 距离）
    -- 新内容入库时计算一次，信源价值评估时直接聚合
```

---

## 8. API 设计

### 8.1 认知驱动发现

```
POST   /api/v1/intelligence/discover/{node_id}          # 触发节点的认知驱动信源发现
POST   /api/v1/intelligence/discover/cluster/{cluster_id} # 触发簇级信源发现
GET    /api/v1/intelligence/discover/{node_id}/strategy   # 查看节点的当前搜索策略
GET    /api/v1/intelligence/discover/stream               # SSE 实时发现进度（扩展现有 SSE）
```

### 8.2 情报缺口

```
GET    /api/v1/intelligence/coverage/{node_id}            # 查看节点覆盖度报告
GET    /api/v1/intelligence/coverage/cluster/{cluster_id}  # 查看簇覆盖度全景
GET    /api/v1/intelligence/gaps                           # 查看所有缺口列表（按严重度排序）
POST   /api/v1/intelligence/gaps/{gap_id}/fill             # 手动触发缺口补充
POST   /api/v1/intelligence/coverage/{node_id}/recalculate # 手动触发节点覆盖度重算
POST   /api/v1/intelligence/coverage/recalculate           # 手动触发全局覆盖度重算
```

### 8.3 信源价值评估

```
GET    /api/v1/intelligence/sources/{source_id}/value      # 查看信源情报价值
GET    /api/v1/intelligence/sources/ranking                 # 信源价值排行榜
POST   /api/v1/intelligence/sources/evaluate                # 手动触发全量评估
```

### 8.4 情报感知与洞察

```
# 信号
GET    /api/v1/intelligence/signals/node/{node_id}                     # 查看节点的信号列表
GET    /api/v1/intelligence/signals/cluster/{cluster_id}                # 查看簇的信号列表

# 洞察
GET    /api/v1/intelligence/insights/node/{node_id}                    # 查看节点的洞察时间线
GET    /api/v1/intelligence/insights/cluster/{cluster_id}              # 查看簇的洞察聚合
GET    /api/v1/intelligence/insights/{insight_id}                      # 查看洞察详情
POST   /api/v1/intelligence/insights/{insight_id}/feedback             # 提交洞察反馈（有价值/噪音）
POST   /api/v1/intelligence/insights/{insight_id}/ask                  # 追问洞察（对话模式）

# 订阅
GET    /api/v1/intelligence/insights/subscriptions                     # 查看我的订阅列表
POST   /api/v1/intelligence/insights/subscriptions                     # 创建订阅
PUT    /api/v1/intelligence/insights/subscriptions/{sub_id}            # 更新订阅（调整推送阈值等）
DELETE /api/v1/intelligence/insights/subscriptions/{sub_id}            # 取消订阅

# 每日摘要
GET    /api/v1/intelligence/digest                                     # 查看今日 medium 洞察汇总
```

### 8.5 情报任务（复用现有审批体系）

```
# 不新增独立的任务 API
# 情报相关的提案通过现有 change_proposals API 管理：
GET    /api/v1/approvals?type=DISCOVER_SOURCES,TARGETED_DISCOVERY,ADJUST_CRAWL_FREQUENCY,DEACTIVATE_SOURCE,REPLACE_SOURCE
POST   /api/v1/approvals/{proposal_id}/approve
POST   /api/v1/approvals/{proposal_id}/reject
# 管理员在同一个审批中心看到所有类型的提案，可按类型筛选
```

---

## 9. 定时任务

| 任务 | 频率 | 说明 |
|------|------|------|
| 覆盖度增量更新 | 事件驱动 | 节点有新内容入库或信源变更时，增量重算该节点覆盖度 |
| 覆盖度全量校准 | 每周 | 全量重算所有节点和簇的覆盖度，校准增量累积误差 |
| 信源价值评估 | 每周 | 计算所有信源的情报价值，生成调整建议 |
| 认知驱动发现 | 每周 | 为缺口节点执行信源发现（按预算和优先级排序） |
| 搜索策略刷新 | 认知模型更新时 | 认知模型变更后自动重新生成搜索策略 |
| 抓取频率调整 | 信源评估后 | 频率决策器综合缺口和价值评估结果，输出最终频率 |
| 情报信号检测 | 事件驱动（内容入库时） | 每篇内容入库后实时检测信号（本地计算，不调用 LLM） |
| 洞察生成 | 事件驱动（信号触发） | 信号严重度 >= medium 时触发 LLM 分析生成洞察 |
| 每日洞察摘要 | 每日 | 汇总当天所有 medium 洞察，推送给订阅用户 |
| 信号清理 | 每周 | 清理 30 天前已处理的低严重度信号 |

---

## 10. 实施路线图

> **前置条件**: 情报网络的所有阶段必须在认知框架（知识图谱簇 + AI 认知模型）上线之后启动。
> 具体来说，认知框架的 Phase 1（数据模型重构）和 Phase 2（AI 认知模型 + 三阶段分类）必须完成，
> 情报网络才有可用的分类结果来计算命中率、覆盖度等指标。

```
Phase 1: 信源价值评估 (1-2 周)
├── 前置：认知框架 Phase 2 已上线（三阶段分类可用）
├── 新增 source_intelligence_values 表
├── 实现五维度评估算法
│   ├── 认知贡献度：基于 embedding 距离衡量新颖度
│   └── 独占性：初期使用 content_hash 精确去重
├── 信源价值仪表盘（前端）
├── 频率决策器（仲裁缺口提频和价值降频）
└── 交付物：能看到每个信源"值不值"，自动调整抓取频率

Phase 2: 情报缺口感知 (2-3 周)
├── 新增 coverage_reports 表
├── content_node_relations 新增 matched_signals、novelty_score 字段
├── 实现覆盖度计算（增量更新 + 每周全量校准 + 手动重算）
├── 权重自适应（AI 推荐 + 管理员覆盖）
├── 缺口识别与提案生成（复用 change_proposals）
├── 簇级覆盖度全景（前端）
└── 交付物：能看到"缺什么"，自动生成补充提案

Phase 3: 认知驱动发现 (2-3 周)
├── 新增 discovery_strategies 表（多态：节点级 + 簇级）
├── knowledge_nodes 新增 embedding 字段
├── 认知模型 → 搜索策略生成服务
├── 多渠道搜索适配器（优先：搜索引擎 + GitHub，其他渠道后续迭代）
├── 认知验证（embedding 相似度为主，LLM 兜底边界案例）
├── 直接替换现有 source_discovery.py，SSE 阶段重新映射
└── 交付物：信源发现从关键词升级为认知驱动

Phase 4: 情报感知与洞察 (2-3 周)
├── 新增 intelligence_signals、intelligence_insights、insight_subscriptions 表
├── 信号检测引擎（内容入库时实时触发，本地计算）
│   ├── CONCEPT_EMERGENCE: 新词频统计
│   ├── CONTENT_SURGE: 日均值对比
│   ├── CROSS_NODE_RESONANCE: 多节点命中检测
│   ├── NOVELTY_SPIKE: embedding 距离异常检测
│   └── SOURCE_PATTERN_SHIFT: 信源主题分布变化
├── 洞察生成服务（信号驱动，LLM 分析）
├── 洞察质量保障（溯源验证、置信度计算）
├── 认知时间线界面（前端）
├── 分级推送 + 每日摘要
├── 洞察追问（对话模式）
└── 交付物：用户收到的是有营养的情报洞察，而非文章列表或定期简报

Phase 5: 闭环整合 (1 周)
├── 缺口 → 发现 → 抓取 → 评估 → 感知的自动化流转
├── 进化信号产出（供第一环认知框架消费）
├── 洞察反馈纳入进化信号
├── 全局情报仪表盘
└── 交付物：完整的情报网络闭环
```

### 风险评估

| 阶段 | 风险 | 缓解 |
|------|------|------|
| Phase 1 | 评估算法的合理性需要实际数据校准 | 先上线收集数据，再迭代调整权重 |
| Phase 2 | 覆盖度模型可能过于理想化 | 初期简化维度（先做数量+时效性），逐步增加 |
| Phase 3 | 多渠道搜索的适配器开发量 | 优先实现搜索引擎 + GitHub，其他渠道后续迭代 |
| Phase 4 | 信号检测产生过多噪音（低价值洞察泛滥） | 严重度分级 + 用户噪音反馈自适应降权 + 信号合并窗口（72h） |
| Phase 5 | 自动化闭环可能产生意外行为 | 所有自动化操作走审批流，逐步放开低风险操作 |

---

## 11. 约束

- **审批机制**: 信源停用、频率大幅调整、新信源添加必须走审批流
- **低风险自动化**: 小幅频率调整（±50%以内）可配置为自动执行
- **发现预算**: 每周最多 N 个节点参与信源发现（默认 20），每个节点每次候选上限 20 个
- **认知验证成本**: 候选信源验证以 embedding 相似度为主（本地计算），仅边界案例调用 LLM（预期 30%）
- **抓取礼貌**: 频率调整有上下限保护（最高 30 分钟/次，最低 7 天/次）
- **数据保留**: 覆盖度报告和价值评估历史保留 90 天，洞察永久保留，已处理的低严重度信号保留 30 天
- **频率仲裁**: 缺口感知和价值评估的频率建议统一由频率决策器仲裁，价值降频优先于缺口提频
- **洞察质量**: 洞察中的事实性陈述必须关联到具体 content_id（可溯源），置信度由信号强度和内容数量计算（不依赖 LLM 自评）
- **信号检测成本**: 信号检测全部为本地计算（词频统计 + embedding 距离 + 计数），不调用 LLM；仅洞察生成阶段调用 LLM
- **噪音控制**: 同类信号 72 小时内合并，用户"噪音"反馈自适应降低同类信号严重度权重

## 12. 成功指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 信源发现命中率 | >60%（发现的信源通过审批的比例） | 审批通过率 |
| 情报缺口响应时间 | < 7 天（从识别缺口到有内容填充） | 缺口生命周期 |
| 高价值信源占比 | >50%（情报价值 > 0.5 的信源比例） | 评估统计 |
| 内容命中率提升 | 从当前基线提升 20% | 分类统计 |
| 人工信源管理工作量 | 减少 50% | 操作次数统计 |
| 洞察有价值率 | >60%（用户反馈"有价值"的比例） | 反馈统计 |
| 洞察信噪比 | <20%（用户标记"噪音"的比例） | 反馈统计 |

---

## Metadata

- 规模: 大
- 涉及模块: `intelligence`, `source`, `crawl_engine`, `evolution`, `ai_facade`
- 涉及端: Backend, Frontend
- 前置依赖: 下一代知识架构（知识图谱簇 + AI 认知模型）
- 创建时间: 2026-02-21
- 状态: 草稿
