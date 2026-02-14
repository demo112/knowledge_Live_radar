# Requirements: 内容新陈代谢系统 (Content Metabolism)

## Overview

内容库目前缺乏清理机制，导致低价值、过时内容堆积，影响系统性能和用户获取信息的效率。本系统旨在建立一套自动化的内容生命周期管理机制（新陈代谢），通过综合评估时间、热度和质量评分，对内容进行阶梯式处理（降权、归档、删除），从而保持知识库的“新鲜”和“高质量”。

核心理念：**优胜劣汰，自动流转，人工兜底。**

## User Stories

### Story 1: 内容生命周期状态管理

As a 系统, I want 给内容标记不同的生命周期状态, so that 可以区分活跃内容和淘汰内容。

**Acceptance Criteria:**
- [ ] AC1: 定义生命周期状态
  - **Given**: 系统初始化
  - **When**: 查看内容模型
  - **Then**: 内容项包含 `lifecycle_status` 字段，枚举值为：
    - `ACTIVE`: 活跃（默认）
    - `DEPRECATED`: 降权（搜索排名降低，不主动推荐）
    - `ARCHIVED`: 归档（搜索不可见，仅后台/历史记录可见）
    - `DELETED`: 软删除（回收站，30天后物理删除）

### Story 2: 综合评分与自动流转 (The Metabolism Engine)

As a 系统, I want 根据综合策略自动更新内容状态, so that 减少人工维护成本。

**Acceptance Criteria:**
- [ ] AC1: 计算代谢分 (Metabolism Score)
  - **Given**: 一个内容项
  - **When**: 每日跑批计算
  - **Then**: 系统根据以下公式计算代谢分：
    - 基础分：AI 质量评分 (0-100)
    - 时间衰减：`exp(-天数 / 半衰期)`
    - 热度加权：`log(点击量 + 引用量 + 1)`
  
- [ ] AC2: 自动降权 (Active -> Deprecated)
  - **Given**: 内容状态为 `ACTIVE`
  - **When**: 代谢分低于阈值 T1 (e.g., 40) 且 发布时间 > 30天
  - **Then**: 状态自动更新为 `DEPRECATED`，记录日志

- [ ] AC3: 自动归档 (Deprecated -> Archived)
  - **Given**: 内容状态为 `DEPRECATED`
  - **When**: 连续 30 天无访问/引用 且 发布时间 > 90天
  - **Then**: 状态自动更新为 `ARCHIVED`

### Story 3: 清理建议报告 (Suggestion Mode)

As a 管理员, I want 收到待清理内容的建议列表, so that 我可以确认是否真的删除。

**Acceptance Criteria:**
- [ ] AC1: 生成建议列表
  - **Given**: 存在一批低质量内容（如 AI 评分 < 30 或 包含大量乱码）
  - **When**: 每日清理任务执行时
  - **Then**: 
    - 系统识别出“高风险删除对象”（如判定为广告、完全无关内容）
    - 生成一份 `MetabolismReport`，包含待删除内容的摘要和原因
    - 发送通知/在仪表盘提示管理员

- [ ] AC2: 批量处理建议
  - **Given**: 管理员查看建议列表
  - **When**: 管理员勾选并点击“确认清理”
  - **Then**: 选中的内容被标记为 `DELETED`

### Story 4: 物理删除 (Garbage Collection)

As a 系统, I want 彻底删除回收站中的陈旧数据, so that 释放数据库空间。

**Acceptance Criteria:**
- [ ] AC1: 自动物理删除
  - **Given**: 内容状态为 `DELETED`
  - **When**: 状态更新时间超过 30 天
  - **Then**: 从数据库中物理删除该记录及其关联数据（如向量索引、关系边）

## Constraints

- **性能要求**: 每日跑批任务应在低峰期（如凌晨 3:00）执行，且不影响前台查询性能。
- **数据安全**: `ARCHIVED` 状态的内容必须保留在数据库中，以备审计或恢复。
- **误删保护**: 物理删除前必须经过 `DELETED` (软删除) 缓冲期。

## Out of Scope

- 用户端的手动“不感兴趣”反馈机制（这是推荐系统的一部分）。
- 复杂的内容版本控制（目前只管理当前版本的生命周期）。

## Assumptions

- 系统已存在 AI 质量评分机制（`SoftValidator`）。
- 系统有记录内容访问/引用计数的基础设施（如 `HotspotManager` 或 `ContentItem` 字段）。
