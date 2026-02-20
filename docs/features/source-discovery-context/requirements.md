# Requirements: 基于金字塔语境的信息源发现优化

## Overview

目前的信息源发现（Source Discovery）机制是基于金字塔的叶子节点逐个进行关键词搜索。这种方式导致检索到的结果往往是具体的文章或片段，且缺乏对金字塔整体结构和关键分支的理解。

本需求旨在重构信息源发现逻辑，引入**自适应语境感知（Adaptive Context Awareness）**机制。系统将分析金字塔的整体结构（包括核心领域、关键分支、新兴叶子节点），智能生成多维度的搜索查询策略（宏观/中观/微观），从而发现更具价值的信息源。

## User Stories

### Story 1: 自适应语境与多维度查询生成

As a 用户, I want 系统根据金字塔的结构特征智能生成搜索策略, so that 搜索结果既能覆盖整体领域，又能关注关键子领域和新兴技术点

**Acceptance Criteria:**

- [ ] AC1: 全结构语境提取
  - **Given**: 一个已存在的金字塔，包含完整的层级结构（Nodes, Levels, Relationships）
  - **When**: 触发信息源发现任务
  - **Then**: 系统能够提取金字塔的结构快照（Structure Snapshot），包括名称、描述、核心分支（L2-L4）以及具有代表性的叶子节点
  - **Note**: 需考虑 Token 限制，对过大的金字塔进行结构摘要

- [ ] AC2: 多维度查询策略生成
  - **Given**: 提取到的金字塔结构快照
  - **When**: 生成搜索查询
  - **Then**: 系统基于 AI 分析，生成混合粒度的搜索查询组合：
    - **宏观（Macro）**: 针对金字塔整体领域（如 "{Pyramid} 官方文档", "{Pyramid} 最佳实践"）
    - **中观（Meso）**: 针对核心子树或关键分支（如 "{Branch} 架构设计", "{Branch} 深度解析"）
    - **微观（Micro）**: 针对特定新兴技术点或高权重叶子节点（如 "{Node} 最新评测", "{Node} 教程"）

### Story 2: 搜索结果过滤与质量提升

As a 用户, I want 搜索结果是高质量的信息源站点, so that 我能订阅该源的后续更新

**Acceptance Criteria:**

- [ ] AC1: 结果相关性过滤
  - **Given**: 搜索引擎返回的一组 URL
  - **When**: 处理搜索结果
  - **Then**: 系统应优先保留主域名、专栏主页、文档首页等类型的 URL，过滤掉具体的长尾文章页（如果可能）

- [ ] AC2: 提案生成
  - **Given**: 经过过滤的有效 URL
  - **When**: 生成审批提案
  - **Then**: 提案的 `reason` 字段应说明该源与金字塔整体语境的相关性（例如："基于金字塔核心领域 '{Domain}' 发现"）

## Constraints

- **成本控制**: 如果使用 LLM 生成查询，需注意 Token 消耗，或提供基于规则的兜底方案。
- **搜索配额**: 需遵守 DuckDuckGo 或其他搜索引擎的速率限制。
- **兼容性**: 新逻辑应替换原有的 `_get_keywords` 逐个节点搜索的逻辑。

## Out of Scope

- 对搜索到的源进行自动 RSS 探测（这是下一步 `Source Service` 的职责，本需求只负责发现 URL）。
- 对源的具体内容进行深度爬取和分析（这是 `Crawl Engine` 的职责）。

## Assumptions

以下假设已与用户确认：
- [x] 用户更倾向于发现“站点”或“专栏”而非单篇文章。
- [x] 金字塔的 Name 和 Description 是准确且有意义的。

## Metadata

- 规模：小
- 涉及模块：`source_discovery`, `ai_core`
- 涉及端：Backend
- 创建时间：2026-02-20
- 状态：待确认
