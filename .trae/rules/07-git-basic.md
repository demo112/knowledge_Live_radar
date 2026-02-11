# Git 基础规范

## 核心规则

1. **禁止 `git add .`** — 必须精准暂存：`git add <文件>` 或 `git add -p`
2. **全中文 commit** — 禁止英文动词如 Update/Fix/Add
3. **强制 `--no-pager`** — 所有 git 命令必须加，防止卡住
4. **Push 前编译** — `npm run build`

## 精准暂存流程

```bash
git --no-pager status          # 查看变更
git --no-pager diff            # 查看内容
git add <具体文件>              # 精准暂存
git --no-pager diff --staged   # 确认暂存
git commit -m "类型(范围): 中文描述"
```

## 暂存判断

| 变更类型 | 处理 |
|----------|------|
| 本任务代码 | ✅ 暂存 |
| 顺手修复 | ❌ 单独提交 |
| 调试代码 | ❌ 删除 |

## Commit 格式

`<type>(<scope>): <中文描述>`

Type: feat/fix/refactor/docs/test/chore
