# Git 冲突处理规范

## 拉取规范

- **工作前必须拉取**：`git pull --rebase origin main`
- **拉取前确保干净**：有修改先 `git stash`
- **优先 rebase**：保持线性历史

## 冲突处理原则

- **禁止盲目接受任一方**，必须理解双方意图
- AI 判断必须基于 `requirements.md`
- 复杂冲突需人工决策

## 复杂度分类

| 复杂度 | 条件 | AI 处理 |
|--------|------|---------|
| 简单 | import/格式差异 | ✅ 自动 |
| 中等 | 同函数修改/配置 | ⚠️ 需确认 |
| 复杂 | 业务逻辑/架构 | ❌ 人工 |

## 解决后验证

```bash
git --no-pager diff | grep -E "^(<<<<<<<|=======|>>>>>>>)"
npm run build
```

## 放弃解决

```bash
git rebase --abort
git merge --abort
```
