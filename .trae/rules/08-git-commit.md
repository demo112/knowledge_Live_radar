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
- `packages/server/src/modules/user/*` → user
- `packages/server/src/common/*` → common
- `packages/web/src/*` → web
- `packages/app/src/*` → app

## 示例
```
feat(attendance): 新增GPS打卡位置校验功能

背景: 防止远程虚假打卡
变更: 新增LocationValidator，集成校验逻辑
影响: 打卡接口新增位置参数校验
```
