# 并发编辑检测规则

## 核心理念

> **开始前检查，冲突前预防** —— 在修改文件前检测是否有其他人正在修改，避免冲突。

---

## 检测时机

### 必须检测的场景

| 场景 | 说明 |
|------|------|
| 开始新任务 | 任务涉及的文件是否有人修改过 |
| 修改公共代码 | 共享组件、shared 类型 |
| 修改跨模块文件 | 涉及多人负责的模块 |
| 长时间未同步 | 超过 4 小时未 pull |

### 检测命令

```bash
# 检查文件最近 24 小时的修改记录
git log --since="24 hours ago" --oneline -- <file>

# 检查文件最近的修改者
git log -1 --format="%an %ar" -- <file>

# 检查是否有未拉取的远程更新
git fetch origin main
git log HEAD..origin/main --oneline
```

---

## 检测流程

### 开始任务前

```
1. 执行 git fetch origin main
2. 检查目标文件最近 24 小时修改记录
3. 如果有修改：
   - 显示修改者和修改内容
   - 询问是否继续
4. 如果无修改：继续任务
```

### 检测结果处理

| 检测结果 | 处理方式 |
|----------|----------|
| 无人修改 | 继续任务 |
| 有人修改，已合并 | 先 pull，确认理解后继续 |
| 有人修改，未合并 | 暂停，提示用户先同步 |
| 有冲突风险 | 暂停，建议与相关人员沟通 |

---

## AI 行为规范

### 任务开始时输出

```markdown
**并发编辑检测** 🔍

检测文件：
- `packages/web/src/pages/shift/ShiftPage.tsx`
- `packages/server/src/modules/attendance/shift.service.ts`

检测结果：
| 文件 | 最近修改 | 修改者 | 状态 |
|------|----------|--------|------|
| ShiftPage.tsx | 2 小时前 | Trae AI | ⚠️ 需确认 |
| shift.service.ts | 3 天前 | admin | ✅ 安全 |

**建议**：ShiftPage.tsx 最近有修改，建议先 pull 并确认理解后再继续。
```

### 发现冲突风险时

```markdown
⚠️ **并发编辑风险**

文件 `{file}` 在最近 24 小时内被 `{author}` 修改过。

**修改内容**：
{commit message}

**建议操作**：
1. 先执行 `git pull --rebase origin main`
2. 查看修改内容，确认理解
3. 如有疑问，与 {author} 沟通后再继续

是否继续？
```

---

## 高风险文件清单

以下文件历史上发生过多次冲突，需特别注意：

| 文件 | 风险原因 | 检测频率 |
|------|----------|----------|
| `packages/shared/src/types/index.ts` | 多人同时修改类型 | 每次修改前 |
| `packages/web/src/providers/*.tsx` | 全局 Provider | 每次修改前 |
| `packages/web/src/components/common/*.tsx` | 共享组件 | 每次修改前 |
| `docs/task-backlog.md` | 任务状态更新 | 每次修改前 |
| `prisma/schema.prisma` | 数据模型 | 每次修改前 |

---

## 与 Git 规则的关系

本规则是 `07-git-basic.md` 的补充：

- `07-git-basic.md`：规范 Git 操作流程
- 本规则：在操作前增加并发检测

执行顺序：
```
并发检测 → 确认安全 → Git 操作（pull/commit/push）
```

---

## 历史案例

### 案例 1：ToastProvider 冲突

```
时间线：
14:06 - Trae AI 修改 ToastProvider
14:09 - admin 也在修改 ToastProvider
14:30 - 合并时发生冲突

根本原因：双方都没有检测对方是否在修改
```

### 案例 2：ShiftModal 反复修改

```
时间线：
12:05 - Trae AI 完成 ShiftModal
12:28 - Trae AI 再次修改 ShiftModal
14:06 - 合并冲突
14:30 - admin 解决冲突

根本原因：短时间内多次修改同一文件，没有及时同步
```

### 正确做法

```
1. 修改前检查：git log --since="24 hours ago" -- <file>
2. 发现有修改：先 pull，确认理解
3. 修改完成后：及时 commit 和 push
4. 长时间任务：定期 pull 保持同步
```
