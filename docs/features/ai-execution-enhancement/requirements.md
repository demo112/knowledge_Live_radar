# Requirements: AI 驱动的进化建议执行

## Overview

增强系统的进化建议功能，使其不仅能提出问题（如“缺少描述”），还能提供可直接执行的解决方案（如自动生成的描述文本）。用户点击“采纳”后，系统应自动应用这些 AI 生成的内容，实现真正的自动化进化。

## User Stories

### Story 1: 自动补充节点分类说明

As a 用户, I want 在采纳“补充分类说明”建议时自动填充描述, so that 我不需要手动编写节点描述

**Acceptance Criteria:**

- [ ] AC1: AI 生成建议时包含描述内容
  - **Given**: AI 检测到节点缺少描述（description 为空）
  - **When**: AI 生成 `update_node` 类型的建议
  - **Then**: 建议的 `params` 中必须包含 `description` 字段，内容为 AI 根据节点名称和上下文生成的描述文本

- [ ] AC2: 执行建议时应用描述
  - **Given**: 用户点击“采纳”一个包含 `description` 的 `update_node` 建议
  - **When**: `SuggestionExecutor` 执行该建议
  - **Then**: 目标节点的 `description` 字段被更新为建议中的内容

- [ ] AC3: 预览生成的描述（可选）
  - **Given**: 前端显示“补充分类说明”建议
  - **When**: 用户查看建议详情
  - **Then**: 用户可以看到 AI 预生成的描述内容

### Story 2: 自动补充内容入口

As a 用户, I want 在采纳“补充内容入口”建议时自动创建信息源或关联, so that 节点可以开始获取内容

**Acceptance Criteria:**

- [ ] AC1: 识别内容缺失并建议添加源
  - **Given**: AI 检测到节点内容空缺且无关联信息源
  - **When**: AI 生成建议
  - **Then**: 生成 `add_source` 或 `create_node` 类型的建议，旨在建立内容获取通道

- [ ] AC2: 自动配置信息源
  - **Given**: 建议类型为 `add_source`
  - **When**: 用户采纳建议
  - **Then**: 系统自动创建一个新的 `InformationSource`，或将现有源关联到该节点

## Constraints

- **上下文感知**: AI 生成的描述必须基于节点名称、父节点语义、兄弟节点关系以及整个金字塔的主题，严禁脱离上下文生成通用废话。
- **结构稳定性**: 执行建议（特别是 `update_node`）时，严禁修改节点的层级关系、父子关系，除非明确为 `move_node` 或 `split_node` 类型。
- **工程化约束**: 所有 AI 生成的内容必须符合预定义的格式规范，且不能破坏现有的数据完整性。
- **性能**: 描述生成不应显著增加分析阶段的耗时。
- **质量**: AI 生成的描述必须准确、通顺，符合节点语义。
- **安全**: 自动执行的操作必须经过权限校验。

## Out of Scope

- 自动爬取内容（这是 `crawl_engine` 的职责，本需求只负责建立入口）
- 复杂的跨节点内容重组

## Assumptions

- 这里的“内容入口”主要指 `InformationSource` 或用于聚合内容的子节点。
- `SuggestionExecutor` 已有基础框架，只需增强对特定参数的支持。
