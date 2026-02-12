# Requirements: 手动增删改查 (Pyramids & Sources)

## Overview

本项目需要支持对“知识金字塔”和“信息源”进行手动的增删改查（CRUD）操作。目前后端已提供基本接口，但前端功能不完整，需要补充相关 UI 和交互逻辑。

## User Stories

### Story 1: 知识金字塔 CRUD

As a 用户, I want 能够手动创建、查看、修改和删除知识金字塔, so that 我可以灵活管理我的知识体系。

**Acceptance Criteria:**

- [ ] AC1: 创建金字塔
  - **Given**: 用户在金字塔列表页面
  - **When**: 点击“新建金字塔”按钮，填写名称和描述并提交
  - **Then**: 系统调用 `POST /api/v1/pyramids`，创建成功后刷新列表并显示新金字塔

- [ ] AC2: 查看金字塔列表
  - **Given**: 系统中已存在金字塔
  - **When**: 进入金字塔列表页面
  - **Then**: 列表正确显示所有金字塔的名称、描述和创建时间

- [ ] AC3: 修改金字塔
  - **Given**: 用户在金字塔详情或列表页面
  - **When**: 点击“编辑”按钮，修改名称或描述并保存
  - **Then**: 系统调用 `PUT /api/v1/pyramids/{id}`，保存成功后刷新页面内容

- [ ] AC4: 删除金字塔
  - **Given**: 用户在金字塔列表页面
  - **When**: 点击“删除”按钮并确认
  - **Then**: 系统调用 `DELETE /api/v1/pyramids/{id}`，删除成功后从列表中移除该项

### Story 2: 信息源 CRUD

As a 用户, I want 能够手动管理信息源, so that 我可以控制数据的来源。

**Acceptance Criteria:**

- [ ] AC1: 添加信息源
  - **Given**: 用户在信息源管理页面
  - **When**: 输入 URL 并点击“发现”，系统自动填充信息，点击“提交”
  - **Then**: 系统调用 `POST /api/v1/sources`，添加成功后出现在列表中

- [ ] AC2: 查看信息源列表
  - **Given**: 系统中已存在信息源
  - **When**: 进入信息源管理页面
  - **Then**: 列表显示名称、URL、类型、状态及上次抓取时间

- [ ] AC3: 修改信息源
  - **Given**: 用户在信息源管理页面
  - **When**: 点击“编辑”按钮，修改名称、URL 或类型并保存
  - **Then**: 系统调用 `PUT /api/v1/sources/{id}`，保存成功后刷新列表

- [ ] AC4: 删除信息源
  - **Given**: 用户在信息源管理页面
  - **When**: 点击“删除”按钮并确认
  - **Then**: 系统调用 `DELETE /api/v1/sources/{id}`，删除成功后从列表中移除

## Constraints

- 响应式设计：在不同屏幕尺寸下均可正常操作
- 错误处理：API 调用失败时应显示友好提示
- 确认机制：删除操作必须经过用户确认

## Out of Scope

- 金字塔节点的复杂拖拽编辑（仅限金字塔本身的 CRUD）
- 批量导入/导出功能

## Assumptions

- 后端 API 已按规范实现并可正常调用
- 用户具有管理权限

## Metadata

- 规模：中
- 涉及模块：pyramid, sources
- 涉及端：Frontend
- 创建时间：2026-02-12
- 状态：待确认
