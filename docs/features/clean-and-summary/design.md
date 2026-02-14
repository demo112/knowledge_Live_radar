# Design: 内容清洗与批量摘要增强

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 内容智能清洗 | API: `POST /api/v1/contents/batch/clean`, Service: `ContentManagementService.batch_clean` |
| Story 2: 批量全量摘要生成 | API: `POST /api/v1/contents/batch/summarize`, Service: `ContentManagementService.batch_summarize` |
| Story 3: 内容库批量管理界面 | Component: `ContentsPage` (Updated), API: `contentApi.batch*` |

## 数据模型

无需修改现有 `ContentItem` 模型，仅需使用现有字段 `summary` 和 `ai_processed`。

## API定义

### POST /api/v1/contents/batch/clean

触发内容清洗任务（物理删除非中文/非AI相关内容）。

**Request:**
```typescript
interface BatchCleanRequest {
  dry_run: boolean // 默认为 false，若为 true 则仅返回预计删除数量
  chinese_ratio_threshold: number // 默认为 0.2
}
```

**Response:**
```typescript
interface BatchCleanResponse {
  success: boolean
  data: {
    total_scanned: number
    deleted_count: number
    details: Array<{ id: string, title: string, reason: string }> // dry_run=true 时返回
  }
}
```

### POST /api/v1/contents/batch/summarize

触发批量摘要生成任务。

**Request:**
```typescript
interface BatchSummarizeRequest {
  target_ids?: string[] // 可选，若提供则仅处理指定ID，否则处理所有
  overwrite: boolean // 默认为 true
}
```

**Response:**
```typescript
interface BatchSummarizeResponse {
  success: boolean
  data: {
    task_id: string // 后台任务ID
    message: string
  }
}
```

### POST /api/v1/contents/batch/delete

批量物理删除内容。

**Request:**
```typescript
interface BatchDeleteRequest {
  ids: string[]
}
```

**Response:**
```typescript
interface BatchDeleteResponse {
  success: boolean
  data: {
    deleted_count: number
  }
}
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| backend/app/schemas/content_management.py | 新增 | `BatchCleanRequest`, `BatchSummarizeRequest`, `BatchDeleteRequest` 定义 |
| backend/app/services/content_management_service.py | 新增 | `ContentManagementService` 类，包含 `batch_clean`, `batch_summarize`, `batch_delete` |
| backend/app/routers/content_management.py | 新增 | `/contents/batch/*` 路由处理 |
| backend/app/main.py | 修改 | 注册 `content_management` router |
| frontend/src/lib/api.ts | 修改 | `contentApi` 增加 `batchClean`, `batchSummarize`, `batchDelete` |
| frontend/src/app/[locale]/(dashboard)/contents/page.tsx | 修改 | 增加 Checkbox, 批量操作栏, 调用批量 API |

## 引用的已有代码

- `backend/app/models/content.py` - `ContentItem`
- `backend/app/services/ai_service.py` - `generate_summary`, `validate_content_soft`
- `backend/app/services/validator/soft_validator.py` - 参考其验证逻辑

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 内容列表页 | 增加批量操作交互 | 低 |
| AI服务 | 批量生成摘要可能触发限流 | 中 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 清洗逻辑位置 | 后端 Service | 涉及大量数据扫描和AI调用，必须在后端异步执行 |
| 批量摘要执行 | BackgroundTasks | 避免阻塞 HTTP 请求，前端轮询或仅展示触发成功 |
| 语言检测 | 正则表达式 | 简单高效，无需调用 AI |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 误删数据 | 数据丢失 | 提供 `dry_run` 模式；前端二次确认 |
| AI 费用激增 | 成本过高 | 清洗逻辑先执行正则过滤（免费），再执行 AI 过滤（付费） |

## 需要人决策

- [ ] 批量摘要是否默认覆盖旧摘要？(已确认: 是)
- [ ] 语言检测阈值 20% 是否合适？(已确认: 是)
