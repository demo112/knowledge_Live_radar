
## 7. 内容管理 (Content Management)

### 触发新陈代谢
- **POST** `/content-management/metabolism/run`
- **Response**: `{ processed: number, to_deprecated: number, to_archived: number }`

### 获取清理建议
- **GET** `/content-management/metabolism/suggestions`
- **Query**: `limit`
- **Response**: `{ items: Suggestion[] }`

### 执行清理
- **POST** `/content-management/metabolism/cleanup`
- **Body**: `{ ids: string[] }`
- **Response**: `{ deleted_count: number }`
