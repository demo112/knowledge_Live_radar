# 公共代码规则

## 公共代码范围

### 核心公共代码（严格保护）
- `packages/server/src/common/**/*`
- `packages/server/src/types/common.ts`
- `packages/web/src/types/common.ts`
- `packages/web/src/utils/common.ts`
- `packages/app/src/types/common.ts`
- `packages/app/src/utils/common.ts`

### 共享组件（保护）
- `packages/web/src/components/common/**/*`
- `packages/web/src/contexts/**/*`
- `packages/web/src/providers/**/*`
- `packages/app/src/components/common/**/*`
- `packages/app/src/contexts/**/*`

### 共享类型（协调保护）
- `packages/shared/src/types/**/*`

## 修改规则

| 规则 | 说明 |
|------|------|
| 禁止AI自行修改 | AI不得自行修改公共代码 |
| 修改前必须沟通 | 需要修改时，先告知用户 |
| 获得确认后修改 | 用户确认后才能修改 |
| 修改后通知 | 修改后通知所有相关人员 |

## 共享组件特别规则

### 高频冲突组件（历史教训）

以下组件曾发生多人同时修改导致冲突，需特别注意：

| 组件 | 位置 | 说明 |
|------|------|------|
| ToastProvider | `web/src/providers/` | 全局 Toast 提示 |
| StandardModal | `web/src/components/common/` | 标准弹窗 |
| ShiftModal | `web/src/pages/shift/components/` | 班次弹窗（多页面使用） |

### 修改前检查

修改共享组件前，必须执行：

```bash
# 检查最近 24 小时是否有人修改过
git log --since="24 hours ago" --oneline -- <file>

# 检查是否有未合并的修改
git --no-pager status
```

## AI 需要修改时

```
⚠️ 需要修改公共代码

文件: xxx
原因: xxx
修改内容: xxx
影响范围: xxx

**冲突风险检查**:
- 最近 24 小时修改记录: {有/无}
- 其他人正在修改: {是/否}

请确认是否允许修改。
```

## Shared 类型修改规则

### 修改前检查

1. **命名冲突检查**：确认类型名是否已存在
2. **影响范围检查**：确认哪些模块使用了该类型
3. **兼容性检查**：确认修改是否向后兼容

### 修改流程

1. 先在 `design.md` 中声明类型变更
2. 获得用户确认后再修改 shared 类型
3. 修改后同步更新所有使用方

### 历史案例

```
问题：EmployeeStatus 类型冲突
原因：sasuke 和 naruto 都定义了同名类型
解决：重命名为 EmployeeWorkStatus 避免冲突
教训：修改 shared 类型前需检查命名冲突
```
