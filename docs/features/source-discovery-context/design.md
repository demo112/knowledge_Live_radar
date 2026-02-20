# Design: 基于金字塔语境的信息源发现优化

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 结构快照提取 | Service: `SourceDiscoveryService._get_structure_snapshot()` 提取金字塔树状结构（JSON） |
| Story 1: 自适应查询生成 | AI Processor: `DiscoveryProcessor.generate_adaptive_queries()`, Prompt: `discovery/adaptive_query_generation` |
| Story 2: 结果过滤 | Service: `SourceDiscoveryService._filter_results()` 基于域名规则过滤 |
| Story 2: 提案生成 | Service: `SourceDiscoveryService.discover()` 创建 Approval，Reason 包含语境信息 |

## 数据模型

无新增数据模型。复用现有的 `Pyramid`, `PyramidNode`, `Approval`, `InformationSource`。

## API定义

无需修改现有 API 签名，仅修改内部实现逻辑。

### POST /api/v1/sources/discover

触发信息源发现任务。

**Request:**
```typescript
interface DiscoverRequest {
  pyramid_id?: string // UUID
}
```

**Response:**
```typescript
interface SuccessResponse {
  data: {
    message: string
    count: number
  }
}
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/services/source_discovery.py` | 修改 | 重构 `discover` 逻辑，移除 `_get_keywords`，新增 `_get_structure_snapshot` 和 `_filter_results` |
| `backend/app/core/ai/processors/discovery.py` | 新增 | `DiscoveryProcessor` 类，实现 `generate_adaptive_queries` 方法 |
| `backend/app/core/ai/facade.py` | 修改 | 暴露 `discovery_processor` |
| `prompts/discovery/adaptive_query_generation.md` | 新增 | 自适应搜索查询生成的 Prompt 模板 |

## 详细设计

### 1. 结构快照提取 (`_get_structure_snapshot`)

从 `Pyramid` 和 `PyramidNode` 表中构建树状结构：
- **Root**: Pyramid Name & Description
- **L1-L3 Nodes**: Name, Description (if meaningful)
- **Leaf Nodes (Optional)**: High priority or recent ones (limit total tokens)
- **Output**: Simplified JSON Tree String

### 2. 自适应查询生成 (`DiscoveryProcessor`)

**Prompt 模板 (`prompts/discovery/adaptive_query_generation.md`):**

```markdown
---
model: deepseek-chat
temperature: 0.7
---

# Role
你是一个技术研究策略专家，擅长根据知识体系的结构制定信息检索策略。

# Context
用户正在为一个名为 "{{ pyramid_name }}" 的知识金字塔寻找高质量的信息源。
以下是金字塔的结构快照（包含核心分支和关键节点）：
```json
{{ pyramid_structure_json }}
```

# Task
分析上述金字塔结构，制定一个**多维度的信息源搜索策略**。
请生成 3-5 个搜索查询配置，覆盖以下三个维度（视情况组合）：
1. **宏观（Macro）**: 针对整体领域（如官方文档、Awesome列表、社区入口）。
2. **中观（Meso）**: 针对关键子树或分支（如某个特定技术栈的深度解析）。
3. **微观（Micro）**: 针对具有代表性的、新兴的或复杂的具体节点（如最新评测、实战教程）。

# Output Format
JSON List of objects:
[
  {
    "query": "搜索关键词",
    "intent": "寻找官方文档/技术博客/社区讨论/...",
    "scope": "Macro/Meso/Micro",
    "reason": "分析原因（例如：'发现 Rust Async 是一个复杂的子领域，需要专门的深入教程'）"
  },
  ...
]
```

### 3. 结果过滤 (`_filter_results`)

- **规则1**: 优先保留 `scheme + netloc` 级别的 URL 或路径层级较少的 URL。
- **规则2**: 过滤掉常见的非内容站点（如 baidu.com, google.com, github.com(非io), etc. - 视情况而定，github repo 其实是好的源，但 search result 往往是具体 issue）。
- **规则3**: 去重。

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 信息源发现 | 逻辑完全替换，不再基于叶子节点搜索 | 中 |
| 发现速度 | LLM 分析结构耗时稍长，但生成的查询更精准，总体效率可控 | 低 |

## 技术决策

- **Token 限制**: 金字塔结构可能很大，`_get_structure_snapshot` 需限制深度（如 Max Depth=3）或节点总数（如 Max Nodes=50），优先保留 L1/L2 和部分高权重叶子。

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| LLM 生成查询失败 | 无法执行搜索 | 降级为规则拼接：`"{pyramid_name} (blog OR docs)"` |
| 搜索结果过少 | 发现不了源 | 提示用户手动添加或优化金字塔描述 |

## 需要人决策

- [ ] 是否需要保留旧的"基于叶子节点搜索"作为选项？（当前设计为直接替换）
