# Design: 审批中心增强 (Approval Center Enhancement)

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 批量审批提案 | API: `POST /api/v1/approvals/batch/review`<br>Frontend: `ApprovalList.tsx` 增加多选和批量操作栏 |
| Story 2: 清理所有待审批项 | API: `POST /api/v1/approvals/cleanup`<br>Frontend: `ApprovalList.tsx` 增加清理按钮 |
| Story 3: 黑暗模式 UI 修复 | Frontend: `ApprovalList.tsx` 调整 Tailwind 类名，适配 dark mode |

## 数据模型

无需修改数据库 Schema。复用现有的 `Approval` 模型。

## API定义

### 1. 批量审批

**POST /api/v1/approvals/batch/review**

批量处理指定的审批提案。

- action="approve": 执行通过操作，状态变为 Approved。
- action="reject": 执行拒绝操作，从数据库物理删除。

**Request:**

```python
class BatchReviewRequest(BaseModel):
    ids: List[UUID]
    action: str  # "approve" | "reject"
    reason: Optional[str] = "Batch operation"
```

**Response:**

```python
class BatchReviewResult(BaseModel):
    success_count: int
    failure_count: int
    failures: List[Dict[str, Any]] # [{"id": "...", "error": "..."}]
```

### 2. 清理所有待审批项

**POST /api/v1/approvals/cleanup**

将所有状态为 `pending` 的提案物理删除。

**Request:**

```python
class CleanupRequest(BaseModel):
    reason: str = "Batch Cleanup"
```

**Response:**

```python
class CleanupResult(BaseModel):
    count: int
    message: str
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/schemas/approval.py` | 修改 | 新增 `BatchReviewRequest`, `BatchReviewResult`, `CleanupRequest`, `CleanupResult` |
| `backend/app/services/approval_service.py` | 修改 | 新增 `batch_review`, `cleanup_pending_approvals` 方法 |
| `backend/app/routers/approvals.py` | 修改 | 新增 `POST /batch/review`, `POST /cleanup` 路由 |
| `frontend/src/lib/api.ts` | 修改 | 新增 `approvalApi.batchReview`, `approvalApi.cleanup` 方法 |
| `frontend/src/components/approval/ApprovalList.tsx` | 修改 | 实现多选逻辑、批量操作栏、清理按钮、修复 Dark Mode 样式 |

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 单条审批 | 无直接影响，逻辑复用 | 低 |
| 审批列表 | UI 结构变化（增加 checkbox 和操作栏） | 低 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 批量执行策略 | 串行执行 | 简单可靠，目前并发量不大，失败可单独处理。若量大后续可改为后台任务。 |
| 清理操作语义 | 批量拒绝 (Reject) | 保留历史记录，比物理删除更安全，符合审计要求。 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 批量操作部分失败 | 用户困惑 | 返回详细的失败列表，前端展示哪些成功哪些失败。 |
| 清理操作误触 | 数据丢失（状态变更） | 前端增加二次确认弹窗 (Confirm Dialog)。 |

## 需要人决策

- [x] 确认清理操作定义为“批量拒绝”。
- [x] 确认批量操作使用统一理由。
