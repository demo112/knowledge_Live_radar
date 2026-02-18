# Design: AI 驱动的进化建议执行增强

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 自动补充节点分类说明 | **Backend**: 优化 Prompt 生成 description, 复用 `update_node` 执行逻辑 |
| Story 2: 自动补充内容入口 | **Backend**: 新增 `add_source` 执行逻辑, 创建 Draft 状态的信息源 |

## 核心变更

### 1. Prompt 工程 (Backend)

修改 `backend/app/core/ai/prompts/pyramid_health_analysis.md`，增强指令：

- **Context Awareness**: 明确要求 AI 在生成建议时，必须基于节点路径（Path）、父节点描述、兄弟节点关系来生成内容。
- **Description Generation**: 当检测到节点缺少描述时，强制在 `params` 中生成 `description` 字段。
- **Source Suggestion**: 当节点内容空缺时，建议添加信息源，并在 `params` 中提供推荐的源名称和类型。

**Prompt 示例片段：**

```markdown
...
5. 对于缺少描述的节点，建议 `update_node`，并在 params 中生成 description。描述必须：
   - 基于节点名称和父节点上下文
   - 简明扼要（50字以内）
   - 说明该节点负责收纳哪类知识
6. 对于内容空缺的节点，建议 `add_source`，并在 params 中提供：
   - name: 推荐的源名称（如“{NodeName} 官方文档”）
   - description: 说明为什么要添加这个源
   - type: 推荐的类型（web/rss）
...
```

### 2. Executor 扩展 (Backend)

修改 `backend/app/services/suggestion_executor.py`：

1.  **注册新 Action**: 在 `action_map` 中添加 `add_source`。
2.  **实现 `_execute_add_source`**:
    *   创建 `InformationSource` 实例。
    *   状态设为 `pending` 或 `active`（如果 AI 只有名称没有 URL，可能需要特殊处理，但目前模型要求 URL 必填，这里可能需要允许空 URL 或生成占位符）。
    *   *决策*：由于 `InformationSource` 通常需要 URL，我们这里创建一个“待配置”的源，或者仅创建一个提示。为了自动化，我们创建一个 `InformationSource`，URL 设为 `http://placeholder.url` 或者在模型中允许为空（需检查模型）。

**检查 `InformationSource` 模型：**
我们需要确认 `url` 字段是否必填。如果必填，AI 无法自动执行 `add_source`（除非它能瞎编一个 URL，但这不好）。
*替代方案*：AI 建议 `create_node` 创建一个子节点作为“内容入口容器”，或者建议 `link_content`。
*用户意图*：用户说“补充内容入口”，可能是指“在界面上显示一个入口”。
*技术选择*：实现 `_execute_add_source`，创建一个状态为 `draft` 的源，URL 可为空（需修改模型）或填入 `pending://configuration`。

### 3. Frontend 展示优化 (Frontend)

修改 `frontend/src/components/pyramid/SuggestionCard.tsx` (假设存在)：

- **预览变更**:
  - 如果 `action_type === 'update_node'` 且 `params.description` 存在，显示：“将更新描述为：{params.description}”
  - 如果 `action_type === 'add_source'`，显示：“将创建信息源：{params.name}”

## 数据模型调整

无需修改数据库 Schema，`AISuggestion.params` 已是 JSON 类型。

## API 定义

无需修改 API 接口。

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| backend/app/core/ai/prompts/pyramid_health_analysis.md | 修改 | 增加 description 生成指令和上下文约束 |
| backend/app/services/suggestion_executor.py | 修改 | 实现 `_execute_add_source`，注册 action_map |
| frontend/src/lib/constants.ts | 修改 | 确保 `add_source` 在 `CHANGE_TYPE_MAP` 中 |

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 建议生成 | 生成耗时可能微增，Token 消耗增加 | 低 |
| 建议执行 | 支持了新的操作类型 | 低 |

## 风险点

- **AI 幻觉**: 生成的描述可能不准确。
  - *应对*: 用户必须审批（Approve）才能执行。
- **URL 缺失**: `add_source` 没有真实 URL。
  - *应对*: 创建的源状态为 `pending`，在前端提示用户去配置。

## 需要人决策

- [ ] `add_source` 执行时，URL 如何处理？
  - A: 设为占位符 `http://pending-configuration`
  - B: 允许模型中 URL 为空（需修改 Schema）
  - *推荐*: A，避免修改 Schema。

