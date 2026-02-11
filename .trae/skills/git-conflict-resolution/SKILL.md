---
name: git-conflict-resolution
description: "git冲突、合并冲突、conflict、冲突解决、rebase冲突、merge冲突、pull冲突"
triggers:
  - git冲突
  - 合并冲突
  - conflict
  - 冲突解决
  - rebase冲突
related_rules:
  - rules/09-git-conflict
next_skills:
  - git-operation (冲突解决后)
---

# Git 冲突解决

处理 Git 拉取、合并过程中产生的冲突，提供系统化的检测、分析、解决和验证流程。

## 核心理念

> **理解优先，最小改动** —— 先理解双方意图，再选择最小影响的解决方案，确保不丢失任何有效代码。

---

## 激活方式

### 触发场景

- `git pull` 产生冲突
- `git rebase` 产生冲突
- `git merge` 产生冲突
- 用户提到"冲突"、"conflict"

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心 | 冲突、conflict、merge失败 |
| 动作 | 解决冲突、处理冲突、合并冲突 |
| 场景 | pull失败、rebase失败、有冲突了 |

### 激活确认

> **Git 冲突解决员已激活** ⚔️
> 
> 检测到冲突，我将帮你：
> 1. 🔍 分析冲突类型和复杂度
> 2. 📋 展示双方改动意图
> 3. 💡 提供解决方案
> 4. ✅ 验证解决结果

---

## 阶段一：冲突检测

### 检测命令

```bash
# 查看冲突状态
git --no-pager status

# 列出所有冲突文件
git --no-pager diff --name-only --diff-filter=U

# 查看冲突详情
git --no-pager diff
```

### 冲突标记识别

```
<<<<<<< HEAD (或 <<<<<<< 当前分支名)
你的本地代码
=======
远程/对方的代码
>>>>>>> 远程分支名 (或 commit hash)
```

### 状态输出模板

```markdown
## 冲突检测结果

| 项目 | 值 |
|------|-----|
| 冲突文件数 | {count} |
| 操作类型 | pull / rebase / merge |
| 当前分支 | {branch} |
| 目标分支 | {target} |

### 冲突文件列表

| 文件 | 冲突块数 | 类型 |
|------|----------|------|
| {path} | {count} | {type} |
```

---

## 阶段二：冲突分析

### 分析维度

| 维度 | 分析内容 | 命令 |
|------|----------|------|
| 双方改动 | 各自做了什么修改 | `git --no-pager log --merge -p <file>` |
| 共同祖先 | 冲突前的原始状态 | `git --no-pager show :1:<file>` |
| 本地版本 | 你的改动 | `git --no-pager show :2:<file>` |
| 远程版本 | 对方的改动 | `git --no-pager show :3:<file>` |

### 冲突类型分类

| 类型 | 特征 | 复杂度 | 处理策略 |
|------|------|--------|----------|
| **内容冲突** | 同一行不同修改 | 中-高 | 需理解意图后合并 |
| **新增冲突** | 同位置各自新增 | 低 | 通常保留双方 |
| **删除冲突** | 一方删除一方修改 | 中 | 需确认是否保留 |
| **重命名冲突** | 同文件不同重命名 | 中 | 需确认最终命名 |
| **二进制冲突** | 二进制文件冲突 | 高 | 需人工选择版本 |

### 复杂度评估

| 复杂度 | 条件 | AI 处理能力 |
|--------|------|-------------|
| **简单** | 新增代码无交集、import 语句、格式差异 | ✅ 可自动处理 |
| **中等** | 同函数不同修改、配置文件、依赖版本 | ⚠️ 需确认后处理 |
| **复杂** | 业务逻辑冲突、架构变更、数据模型 | ❌ 需人工决策 |

### 分析输出模板

```markdown
## 冲突分析：{filename}

### 冲突位置
第 {start_line} - {end_line} 行

### 本地改动（你的）
```{lang}
{your_code}
```
**意图**：{your_intent}

### 远程改动（对方的）
```{lang}
{their_code}
```
**意图**：{their_intent}

### 复杂度评估
- 类型：{type}
- 复杂度：{level}
- AI 可处理：{yes/no}

### 建议方案
{recommendation}
```

---

## 阶段三：冲突解决

### 自主能力边界

#### ✅ 可自动处理（无需确认）

| 场景 | 条件 | 处理方式 |
|------|------|----------|
| import 语句冲突 | 无重复、无循环依赖 | 合并去重 |
| 格式化差异 | 仅空格/换行/缩进 | 按项目规范统一 |
| 注释冲突 | 内容不矛盾 | 保留更完整的 |
| 新增代码无交集 | 不同位置各自新增 | 保留双方 |
| 依赖版本 | 语义化版本兼容 | 取较新版本 |
| 类型定义扩展 | 新增字段不冲突 | 合并字段 |

#### ⚠️ 需确认后处理

| 场景 | 原因 | 处理方式 |
|------|------|----------|
| 同函数不同修改 | 可能影响逻辑 | 展示双方意图，提供合并建议 |
| 配置文件冲突 | 可能影响环境 | 列出差异，请求确认 |
| 测试用例冲突 | 可能影响覆盖 | 展示差异，建议保留双方 |
| 一方删除一方修改 | 需确认是否保留 | 询问保留哪个 |

#### ❌ 必须人工决策

| 场景 | 原因 | 处理方式 |
|------|------|----------|
| 业务逻辑冲突 | 需要业务判断 | 暂停，展示选项 |
| 数据模型冲突 | 影响数据结构 | 暂停，请求决策 |
| 架构变更冲突 | 影响系统设计 | 暂停，请求决策 |
| 安全相关代码 | 风险高 | 暂停，请求决策 |
| 无法理解意图 | 信息不足 | 暂停，请求说明 |

### 解决策略矩阵

| 场景 | 策略 | 操作 |
|------|------|------|
| 双方新增不同功能 | 保留双方 | 合并两段代码 |
| 同一函数不同修改 | 合并逻辑 | 理解后整合 |
| import 语句冲突 | 合并去重 | 保留所有需要的 import |
| 格式化差异 | 统一格式 | 按项目规范格式化 |
| 配置文件冲突 | 按环境合并 | 保留各环境配置 |
| 依赖版本冲突 | 取较新版本 | 选择兼容的较新版本 |
| 一方删除一方修改 | 确认需求 | 询问是否保留 |
| 业务逻辑冲突 | 人工决策 | 暂停，请求用户决策 |

### 解决步骤

```bash
# 1. 打开冲突文件，定位冲突标记
# 2. 理解双方意图
# 3. 编辑文件，删除冲突标记，保留正确代码
# 4. 保存文件

# 5. 标记为已解决
git add <resolved-file>

# 6. 继续操作
git rebase --continue  # 如果是 rebase
git merge --continue   # 如果是 merge
# 或直接 commit        # 如果是 pull
```

### 常见场景解决示例

#### 场景1：import 语句冲突

```typescript
// 冲突前
<<<<<<< HEAD
import { UserService } from './user.service';
import { AuthGuard } from '../guards/auth.guard';
=======
import { UserService } from './user.service';
import { RoleGuard } from '../guards/role.guard';
>>>>>>> origin/main

// 解决后（合并去重）
import { UserService } from './user.service';
import { AuthGuard } from '../guards/auth.guard';
import { RoleGuard } from '../guards/role.guard';
```

#### 场景2：同函数不同修改

```typescript
// 冲突前
<<<<<<< HEAD
async getUserProfile(userId: string) {
  const user = await this.prisma.user.findUnique({
    where: { id: userId },
    include: { department: true }  // 你加的：包含部门
  });
  return user;
}
=======
async getUserProfile(userId: string) {
  const user = await this.prisma.user.findUnique({
    where: { id: userId },
    select: { id: true, name: true, email: true }  // 对方加的：字段筛选
  });
  return user;
}
>>>>>>> origin/main

// 解决后（合并两个需求）
async getUserProfile(userId: string) {
  const user = await this.prisma.user.findUnique({
    where: { id: userId },
    include: { department: true },
    select: { id: true, name: true, email: true, department: true }
  });
  return user;
}
```

#### 场景3：package.json 依赖冲突

```json
// 冲突前
<<<<<<< HEAD
"dependencies": {
  "express": "^4.18.2",
  "lodash": "^4.17.21"
}
=======
"dependencies": {
  "express": "^4.19.0",
  "dayjs": "^1.11.10"
}
>>>>>>> origin/main

// 解决后（取较新版本 + 合并依赖）
"dependencies": {
  "express": "^4.19.0",
  "lodash": "^4.17.21",
  "dayjs": "^1.11.10"
}
```

---

## 阶段四：验证结果

### 验证清单

```bash
# 1. 确认无残留冲突标记
git --no-pager diff | grep -E "^(<<<<<<<|=======|>>>>>>>)"
# 应该无输出

# 2. 确认文件语法正确
npm run build  # 或对应的编译命令

# 3. 确认测试通过
npm run test

# 4. 确认 Git 状态干净
git --no-pager status
# 应该显示 "nothing to commit" 或只有已暂存的文件
```

### 验证输出模板

```markdown
## 冲突解决验证

### 解决结果
| 文件 | 状态 |
|------|------|
| {path} | ✅ 已解决 |

### 验证检查
- [ ] 无残留冲突标记
- [ ] 编译通过
- [ ] 测试通过
- [ ] Git 状态正常

### 下一步
- `git rebase --continue` 继续 rebase
- `git push` 推送代码
```

---

## 特殊场景处理

### Rebase 冲突

```bash
# rebase 过程中的冲突
git rebase origin/main

# 冲突时会暂停，解决后：
git add <resolved-files>
git rebase --continue

# 如果想放弃 rebase：
git rebase --abort

# 如果想跳过当前 commit：
git rebase --skip
```

### 多次冲突（rebase 多个 commit）

```bash
# rebase 可能在多个 commit 处产生冲突
# 每次解决后都要 --continue

# 查看 rebase 进度
git --no-pager status
# 会显示 "rebase in progress; onto {hash}"
```

### Stash 冲突

```bash
# stash pop 产生冲突时
git stash pop

# 解决冲突后，stash 不会自动删除
# 需要手动删除
git stash drop
```

### 放弃解决

```bash
# 放弃 merge
git merge --abort

# 放弃 rebase
git rebase --abort

# 重置到冲突前状态
git reset --hard HEAD
```

---

## 与用户的沟通

### 开始处理时

```
⚔️ 检测到 Git 冲突

发现 {count} 个文件存在冲突，正在分析...

| 文件 | 复杂度 |
|------|--------|
| {path} | {level} |

预计 {auto} 个可自动处理，{manual} 个需要你确认。
```

### 请求确认时

```
🔍 需要你确认这个冲突的解决方案

文件：{path}
位置：第 {line} 行

{展示双方代码和建议方案}

回复：
- "确认" - 使用建议方案
- "用我的" - 保留你的版本
- "用对方的" - 保留对方版本
- 或直接提供你想要的代码
```

### 完成处理时

```
✅ 冲突已解决

- 自动处理：{auto} 个
- 确认处理：{confirm} 个
- 验证结果：编译通过

下一步：
- `git push` 推送代码
- 或继续其他开发工作
```

### 无法处理时

```
⚠️ 这个冲突我无法自动处理

文件：{path}
原因：{reason}

需要你来决定：
1. {option1}
2. {option2}
3. 给我更多上下文信息
```

---

## 安全规则

### 禁止操作

- ❌ `git push --force`（可能丢失他人代码）
- ❌ 删除远程分支
- ❌ 修改已推送的历史
- ❌ 在不理解的情况下随意合并

### 保守原则

- 不确定时，宁可暂停询问
- 涉及业务逻辑，必须人工确认
- 解决后必须验证编译
- 保留完整的处理记录

---

## 异常处理

| 异常 | 处理 |
|------|------|
| 解决后仍有冲突标记 | 重新检查，定位遗漏 |
| 编译失败 | 回滚解决，重新分析 |
| rebase 卡住 | 建议 abort 后用 merge |
| 无法理解冲突 | 暂停，请求人工介入 |

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| git-operation | 本 Skill 是其冲突处理的详细补充 |
| code-verification | 冲突解决后需要验证代码 |
| problem-fixing | 解决后如有问题，转入问题修复 |

---

## 前置条件

- Git 操作产生冲突
- 或用户主动请求处理冲突

## 后续流程

```
git-conflict-resolution 后续：
├── 冲突解决 → 验证编译 → git-operation 继续提交/推送
└── 无法解决 → 暂停，请求人工介入
```
