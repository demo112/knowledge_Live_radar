# API 契约

## 概述

所有 API 均位于 `/api/v1` 路径下。
响应格式遵循统一规范。

### 统一响应格式

```json
// 成功
{
  "success": true,
  "data": { ... }
}

// 失败
{
  "success": false,
  "error": {
    "code": "ERR_MODULE_REASON",
    "message": "Human readable error message"
  }
}
```

## 1. 知识金字塔 (Pyramids)

### 获取金字塔列表
- **GET** `/pyramids`
- **Query**: `page`, `limit`
- **Response**: `{ items: Pyramid[], total: number }`

### 创建金字塔
- **POST** `/pyramids`
- **Body**: `{ name: string, description?: string, template_id?: string }`
- **Response**: `Pyramid`

### 获取金字塔详情
- **GET** `/pyramids/{id}`
- **Query**: `include_tree=true` (是否包含完整节点树)
- **Response**: `Pyramid & { root_node?: NodeTree }`

### 获取金字塔历史快照
- **GET** `/pyramids/{id}/snapshots`
- **Response**: `Snapshot[]`

### 更新金字塔
- **PUT** `/pyramids/{id}`
- **Body**: `{ name?: string, description?: string }`
- **Response**: `Pyramid`

### 删除金字塔
- **DELETE** `/pyramids/{id}`
- **Response**: `{ success: true }`

## 2. 节点管理 (Nodes)

### 创建节点
- **POST** `/nodes`
- **Body**: `{ parent_id: string, name: string, description?: string }`
- **Response**: `PyramidNode`

### 更新节点
- **PUT** `/nodes/{id}`
- **Body**: `{ name?: string, description?: string, sort_order?: number }`
- **Response**: `PyramidNode`

### 删除节点
- **DELETE** `/nodes/{id}`
- **Response**: `{ success: true }`

### 移动节点
- **POST** `/nodes/{id}/move`
- **Body**: `{ new_parent_id: string }`
- **Response**: `PyramidNode`

### 合并节点
- **POST** `/nodes/merge`
- **Body**: `{ source_ids: string[], target_name: string }`
- **Response**: `ChangeProposal` (合并操作需要审批)

## 3. 信息源 (Sources)

### 获取信息源列表
- **GET** `/sources`
- **Query**: `type`, `status`, `page`, `limit`
- **Response**: `{ items: InformationSource[], total: number }`

### 创建信息源
- **POST** `/sources`
- **Body**: `{ name: string, type: 'RSS'|'API'|'WEB', url: string, config: object }`
- **Response**: `InformationSource`

### 更新信息源
- **PUT** `/sources/{id}`
- **Body**: `{ name?: string, config?: object, status?: string }`
- **Response**: `InformationSource`

### 删除信息源
- **DELETE** `/sources/{id}`
- **Response**: `{ success: true }`

### 测试信息源
- **POST** `/sources/{id}/test`
- **Response**: `{ success: true, preview_items: ContentItem[] }`

## 4. 内容与信息流 (Contents & Feed)

### 获取信息流
- **GET** `/feed`
- **Query**: `cursor`, `limit`, `mode` ('fast'|'deep')
- **Response**: `{ items: FeedItem[], next_cursor: string }`

### 搜索内容
- **GET** `/contents`
- **Query**: `q` (keyword), `node_id`, `source_id`, `start_date`, `end_date`, `page`, `limit`
- **Response**: `{ items: ContentItem[], total: number }`

### 获取内容详情
- **GET** `/contents/{id}`
- **Response**: `ContentItem & { validation: ValidationResult, relations: NodeRelation[] }`

### 提交用户贡献
- **POST** `/contents/upload` (Multipart)
- **POST** `/contents/url` (JSON)
- **POST** `/contents/text` (JSON)
- **Response**: `ContentItem`

### 分析内容
- **POST** `/contents/{id}/analyze`
- **Body**: `{ pyramid_id: string }`
- **Response**: `Approval[]`

## 5. 审批中心 (Approvals)

### 获取提案列表
- **GET** `/approvals`
- **Query**: `status`, `type`, `page`, `limit`
- **Response**: `{ items: ChangeProposal[], total: number }`

### 获取提案详情
- **GET** `/approvals/{id}`
- **Response**: `ChangeProposal & { impact_analysis: ImpactReport }`

### 审核提案 (Review)
- **POST** `/approvals/{id}/review`
- **Body**: `{ status: 'approved'|'rejected', review_comment?: string }`
- **Response**: `ChangeProposal`

### 执行提案 (Execute)
- **POST** `/approvals/{id}/execute`
- **Response**: `{ success: true }`

## 6. 健康监控 (Health)

### 获取系统健康报告
- **GET** `/health/system`
- **Response**: `{ overall_score: number, components: { ... } }`

### 获取金字塔健康报告
- **GET** `/health/pyramids/{id}`
- **Response**: `PyramidHealthReport`

### 获取信息源健康报告
- **GET** `/health/sources/{id}`
- **Response**: `SourceHealthReport`
