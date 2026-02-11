# Git Commit 规范

## 格式
```
<type>(<scope>): <标题行>

<正文: 为什么、做了什么、影响什么>
```

## Type
| Type | 场景 |
|------|------|
| feat | 新功能 |
| fix | 修复Bug |
| refactor | 重构 |
| docs | 文档 |
| test | 测试 |
| chore | 构建配置 |
| perf | 性能优化 |

## Scope 识别
- `frontend/src/app/pyramid/*` → pyramid
- `frontend/src/app/feed/*` → feed
- `frontend/src/app/sources/*` → sources
- `frontend/src/app/approval/*` → approval
- `frontend/src/components/*` → components
- `backend/app/routers/*` → api
- `backend/app/services/crawl_*` → crawl
- `backend/app/services/validator/*` → validator
- `backend/app/services/ai_*` → ai
- `backend/app/models/*` → models
- `backend/alembic/*` → migration

## 示例
```
feat(pyramid): 新增金字塔模板创建功能

背景: 支持从预设模板快速创建知识金字塔
变更: 新增 TemplateService，集成5个预设模板
影响: 金字塔创建接口新增 template_id 参数
```
