# Feature: AI 驱动建议系统 (AI Driven Suggestions)

## 1. 概述 (Overview)

当前系统的 AI 建议生成逻辑分散且硬编码，缺乏统一的标准和可执行性。本特性旨在构建统一的 AI 建议生成框架，通过标准化的数据模型 (`AISuggestion`) 和统一的 AI 调用入口 (`AIFacade`)，实现高质量、可执行的智能建议，覆盖金字塔健康、结构重构、内容代谢等核心场景。

## 2. 用户故事 (User Stories)

### Story 1: 统一 AI 建议生成
As a 系统开发者, I want 通过统一的接口生成 AI 建议, So that 消除硬编码逻辑，确保建议格式一致且易于维护。

**Acceptance Criteria (GWT):**

- [ ] AC1: 基于 Prompt 模板生成建议
  - **Given**: 系统需要生成“金字塔健康分析”建议，且已加载 `pyramid_health_analysis.md` 模板
  - **When**: 调用 `SuggestionProcessor.generate(context)`
  - **Then**: 
    - AI 返回符合 `AISuggestion` 结构的 JSON 数据
    - 包含明确的 `action_type` (如 `OPTIMIZE_STRUCTURE`)
    - 包含结构化的 `params` (如 `target_node_id`, `suggested_action`)
    - 不包含任何硬编码的中文描述

- [ ] AC2: 建议持久化与展示
  - **Given**: AI 成功生成了一条优化建议
  - **When**: 系统保存该建议
  - **Then**: 
    - 建议被存储在数据库中，关联到具体的金字塔或节点
    - 前端可以通过统一 API 获取建议列表
    - 建议展示时使用 `i18n` 键值而非硬编码文本

### Story 2: 金字塔健康诊断建议
As a 知识管理员, I want AI 自动诊断金字塔的健康状况并提出行动建议, So that 我能及时发现结构问题（如空节点、低质量内容）。

**Acceptance Criteria (GWT):**

- [ ] AC1: 识别空节点并建议填充
  - **Given**: 金字塔中存在 3 个以上无内容的叶子节点
  - **When**: 触发健康诊断任务
  - **Then**: 
    - 生成 `FILL_EMPTY_NODE` 类型的建议
    - 建议中包含具体的空节点 ID 列表
    - 提供“自动抓取相关内容”或“删除节点”的操作选项

- [ ] AC2: 识别概念漂移并建议重构
  - **Given**: 某节点下的内容与节点定义的语义相似度平均值 < 0.6
  - **When**: 触发健康诊断任务
  - **Then**: 
    - 生成 `RESTRUCTURE_NODE` 类型的建议
    - 指出漂移的内容项
    - 建议拆分节点或移动内容到新节点

## 3. 数据模型 (Data Model)

### AISuggestion (Core)
- `id`: UUID
- `target_id`: UUID (关联实体ID)
- `target_type`: String (PYRAMID, NODE, SOURCE)
- `action_type`: Enum (OPTIMIZE, FIX, PRUNE, EXPAND)
- `priority`: Int (1-100)
- `reason`: String (AI 生成的分析原因)
- `params`: JSON (执行动作所需的参数)
- `status`: Enum (PENDING, ACCEPTED, REJECTED)

## 4. 约束 (Constraints)

- **性能**: 建议生成过程不应阻塞主线程，必须异步执行。
- **一致性**: 所有建议必须通过 `AIFacade` 调用，禁止绕过统一入口。
- **可执行性**: 每个建议必须包含足够的信息（`params`），以便系统或用户执行后续操作。
