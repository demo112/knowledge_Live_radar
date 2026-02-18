# Requirements: 基于金字塔的信息源自动发现

## Overview

系统根据现有知识金字塔（Pyramid）的内容（节点关键词、描述），自动发现相关的高质量中文信息源（RSS/网站），并将其提交给人工审批。审批通过后，自动添加到系统的信息源库中。

## User Stories

### Story 1: 触发信息源发现任务

As a 用户, I want 手动触发信息源发现任务, so that 系统可以帮我寻找新的相关信息源

**Acceptance Criteria:**

- [ ] AC1: 手动触发发现任务
  - **Given**: 用户在信息源管理界面
  - **When**: 用户点击“发现新源”按钮
  - **Then**: 
    - 系统开始后台任务，分析金字塔节点关键词
    - 界面显示“发现任务已启动”提示
    - 任务完成后，若发现新源，通知用户或刷新待审批列表

- [ ] AC2: 自动过滤已存在源
  - **Given**: 系统发现了一个 URL 为 `https://example.com/feed` 的源，但该源已在 `InformationSource` 表中存在
  - **When**: 发现任务执行时
  - **Then**: 该源被自动忽略，不进入待审批列表

### Story 2: 查看待审批源列表

As a 用户, I want 查看系统发现的待审批源, so that 我可以决定是否添加它们

**Acceptance Criteria:**

- [ ] AC1: 显示待审批列表
  - **Given**: 系统已发现 5 个新源，状态为 PENDING
  - **When**: 用户进入信息源管理界面的“发现”标签页
  - **Then**: 
    - 显示这 5 个源的列表
    - 每个源显示：标题、URL、相关性理由（如“与节点X相关”）、发现时间
    - 列表按相关度或发现时间排序

- [ ] AC2: 空状态显示
  - **Given**: 没有待审批的源
  - **When**: 用户进入“发现”标签页
  - **Then**: 显示“暂无待审批的新源”提示

### Story 3: 审批信息源

As a 用户, I want 批准或拒绝系统推荐的源, so that 我可以控制信息源的质量

**Acceptance Criteria:**

- [ ] AC1: 批准源（添加）
  - **Given**: 列表中有一个待审批源 `https://tech.example.com`
  - **When**: 用户点击“添加”或“批准”按钮
  - **Then**: 
    - 该源的状态变为 APPROVED
    - 系统自动创建一个新的 `InformationSource` 记录，状态为 ACTIVE
    - 该源从“待审批”列表中消失（或移至“已通过”历史）
    - 界面提示“已添加源：[源名称]”

- [ ] AC2: 拒绝源
  - **Given**: 列表中有一个无关的源
  - **When**: 用户点击“忽略”或“拒绝”按钮
  - **Then**: 
    - 该源的状态变为 REJECTED
    - 该源从“待审批”列表中消失
    - 系统记录该域名，避免下次重复推荐（可选）

### Story 4: 中文优先策略

As a 用户, I want 系统优先推荐中文源, so that 内容更符合我的阅读习惯

**Acceptance Criteria:**

- [ ] AC1: 搜索偏好中文
  - **Given**: 金字塔节点包含英文术语（如 "LLM"）
  - **When**: 系统执行发现任务
  - **Then**: 搜索策略优先使用中文关键词（如 "LLM 中文博客"、"大模型 技术博客"）或在搜索参数中指定中文语言（`lr=lang_zh`）

## Constraints

- **性能要求**: 发现任务不应阻塞前台操作，应异步执行。
- **去重**: 必须严格去重，避免重复推荐已有的源。
- **质量控制**: 优先推荐支持 RSS 的源，或者内容更新频繁的博客/资讯站。

## Out of Scope

- 自动添加源（必须人工审批）。
- 对非中文源的完全屏蔽（只是优先中文，高质量英文源也可接受，但需用户确认）。
- 自动分类（目前仅作为通用源添加，分类需后续手动调整或自动推断）。

## Assumptions

- 使用现有的 `DiscoveredDomain` 表存储待审批源（需确认是否扩展字段）。
- 使用 AI (LLM) 或 搜索引擎 (Serper/Google) 进行发现。
- 用户已配置好 AI 服务或搜索服务的 API Key。

## Metadata

- 规模: 中
- 涉及模块: `source`, `pyramid`, `discovered_domain`
- 涉及端: Backend, Frontend
