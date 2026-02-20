# Design: Approval Execution & Implementation

## Background

目前系统可以生成变更提案（Approval）并进行审批，但审批通过后缺少自动执行变更的逻辑。特别是对于 AI 生成的“新概念”提案，往往缺少具体的挂载点（父节点），需要 AI 在执行阶段进行决策。

## 需求映射

| Requirement | Implementation |
|-------------|----------------|
| 审批通过后自动执行 | `ApprovalService.execute_approval` |
| AI 决定新节点挂载点 | Prompt: `node_placement.md`, Service: `AIService.find_best_parent_node` |
| 关联内容到节点 | `ApprovalService` 调用 `NodeService` |

## Prompt 设计

### `prompts/approval/node_placement.md`

用于为新节点寻找最佳父节点。

**Input:**
- `new_node_name`: 新节点名称
- `new_node_description`: 新节点描述
- `source_context`: 来源内容上下文
- `candidate_nodes`: 候选父节点列表（简化版金字塔结构）

**Output:**
- `parent_id`: 推荐父节点 ID
- `reason`: 推荐理由

## Service 设计

### `backend/app/services/approval_service.py`

新增 `execute_approval(approval: Approval)` 方法：

```python
async def execute_approval(self, approval: Approval):
    if approval.type == "create_node":
        await self._execute_create_node(approval)
    elif approval.type == "link_content":
        await self._execute_link_content(approval)
    
    # Update status to executed? Or keep approved but log execution?
    # Current model has "approved". We might need "executed" or check if action is done.
    # For now, let's assume "approved" triggers execution, and if successful, we are good.
    # Ideally, we should update status to "executed" or "completed".
```

### `backend/app/services/ai_service.py`

新增 `find_best_parent_node`：

```python
async def find_best_parent_node(self, pyramid_id: str, node_name: str, context: str) -> str:
    # 1. Fetch pyramid structure (simplified)
    # 2. Call LLM with node_placement prompt
    # 3. Return parent_id
```

## API 变更

`PUT /api/v1/approvals/{id}` (Review)

- 当 status 变更为 `approved` 时，添加 `BackgroundTasks` 任务执行 `approval_service.execute_approval(approval_id)`。

## 数据模型变更

`Approval` 模型可能需要新增状态 `executed` 和 `failed`。

```python
# backend/app/models/approval.py
# status: pending, approved, rejected, executed, failed
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `prompts/approval/node_placement.md` | 新增 | 节点挂载决策提示词 |
| `backend/app/services/ai_service.py` | 修改 | 添加 `find_best_parent_node` |
| `backend/app/services/approval_service.py` | 修改 | 添加 `execute_approval` 及具体执行逻辑 |
| `backend/app/routers/approvals.py` | 修改 | 在审批通过后触发异步执行 |
| `backend/app/models/approval.py` | 修改 | (可选) 更新状态枚举文档 |

## 风险分析

- **AI 决策的不确定性**：AI 可能会选择错误的父节点。
    - **Mitigation**: 在 Prompt 中要求 AI 如果找不到合适的，返回根节点或特定“待整理”节点。
- **执行失败**：例如父节点被删除。
    - **Mitigation**: 错误处理，将 Approval 状态置为 `failed` 并记录原因。

