# API 规范

## 路径格式
```
/api/v1/{resource}
/api/v1/{resource}/{id}
/api/v1/{resource}/{id}/{sub-resource}
```

## HTTP 方法
| 方法 | 用途 |
|------|------|
| GET | 查询 |
| POST | 创建 |
| PUT | 全量更新 |
| PATCH | 部分更新 |
| DELETE | 删除 |

## 响应格式（Python Pydantic）
```python
# 成功
class SuccessResponse(BaseModel):
    success: bool = True
    data: Any

# 错误
class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str
    message: str

# 分页
class PaginatedResponse(BaseModel):
    success: bool = True
    data: PaginatedData

class PaginatedData(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
```

## 错误码: `ERR_{MODULE}_{TYPE}`
示例: ERR_PYRAMID_NOT_FOUND, ERR_SOURCE_INVALID_URL, ERR_APPROVAL_ALREADY_PROCESSED

## 状态码
200成功 | 201创建 | 400参数错误 | 401未认证 | 403无权限 | 404不存在 | 422验证失败 | 500服务器错误

## 核心 API 模块

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 金字塔管理 | `/api/v1/pyramids` | CRUD、模板、健康度 |
| 节点管理 | `/api/v1/pyramids/{id}/nodes` | 节点 CRUD、移动、拆分、合并 |
| 信息源管理 | `/api/v1/sources` | CRUD、测试、生命周期 |
| 内容管理 | `/api/v1/contents` | 列表、搜索、详情 |
| 审批管理 | `/api/v1/approvals` | 队列、审批、历史 |
| 健康报告 | `/api/v1/health` | 系统健康、金字塔健康 |
| 系统配置 | `/api/v1/system` | 配置、日志、监控 |
