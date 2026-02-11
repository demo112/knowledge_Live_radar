# 公共代码规则

## 公共代码范围

### 后端核心公共代码（严格保护）
- `backend/app/database.py` - 数据库连接
- `backend/app/config.py` - 配置管理
- `backend/app/utils/**` - 工具函数
- `backend/app/middleware/**` - 中间件

### 前端核心公共代码（严格保护）
- `frontend/src/lib/**` - API 客户端、工具库
- `frontend/src/components/ui/**` - 基础 UI 组件
- `frontend/src/types/**` - 全局类型定义
- `frontend/src/stores/**` - 全局状态管理

### AI 服务模块（特别保护）
- `backend/app/services/ai_service.py` - AI 服务集成
- AI Prompt 模板文件

## 修改规则

| 规则 | 说明 |
|------|------|
| 禁止AI自行修改 | AI不得自行修改公共代码 |
| 修改前必须沟通 | 需要修改时，先告知用户 |
| 获得确认后修改 | 用户确认后才能修改 |
| 修改后验证 | 修改后确保所有依赖模块正常 |

## AI 需要修改时

```
⚠️ 需要修改公共代码

文件: xxx
原因: xxx
修改内容: xxx
影响范围: xxx

请确认是否允许修改。
```
