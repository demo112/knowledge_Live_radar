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

## 响应格式
```typescript
// 成功: { success: true, data: T }
// 错误: { success: false, error: { code: string, message: string } }
// 分页: { success: true, data: { items: T[], total, page, pageSize } }
```

## 错误码: `ERR_{MODULE}_{TYPE}`
示例: ERR_USER_NOT_FOUND, ERR_AUTH_INVALID_TOKEN

## 状态码
200成功 | 201创建 | 400参数错误 | 401未认证 | 403无权限 | 404不存在 | 500服务器错误
