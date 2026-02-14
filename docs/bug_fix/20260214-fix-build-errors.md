# 构建错误修复记录

## 问题描述
- **现象**：前端构建失败，报错 `Module not found: Can't resolve 'date-fns'`，以及后续发现的 `@headlessui/react` 和 `@heroicons/react` 缺失，还有 TypeScript 类型错误。
- **复现步骤**：运行 `pnpm build` 或 `pnpm dev`。
- **影响范围**：前端应用无法启动和构建。

## 设计锚定
- **所属规格**：前端基础设施
- **原设计意图**：项目依赖应该完整定义在 `package.json` 中，类型定义应与后端模型保持一致。
- **当前偏离**：
    1. `package.json` 缺少 `date-fns`, `@headlessui/react`, `@heroicons/react`。
    2. `Approval` 类型定义缺少 `updated_at` 字段，但代码中使用了该字段，且后端模型中存在该字段。

## 根因分析
- **直接原因**：依赖包未安装，类型定义不匹配。
- **根本原因**：可能是开发过程中引入了新库但未提交 `package.json` 变更，或者合并代码时遗漏。类型定义未及时同步后端模型变更。
- **相关代码**：
    - `frontend/package.json`
    - `frontend/src/components/approval/ApprovalHistory.tsx`
    - `frontend/src/components/contribution/ContributionDetailModal.tsx`
    - `frontend/src/types/index.ts`

## 修复方案
- **修复思路**：补全缺失的依赖，同步类型定义。
- **改动文件**：
    - `frontend/package.json` (自动修改)
    - `frontend/pnpm-lock.yaml` (自动修改)
    - `frontend/src/types/index.ts`

## 验证结果
- [x] 原问题已解决：`pnpm build` 成功通过。
- [x] 回归测试通过：构建无报错。
- [x] 设计一致性确认：类型定义与后端模型一致。

## 提交信息
fix(frontend): 修复依赖缺失和类型错误

- 安装缺失依赖: date-fns, @headlessui/react, @heroicons/react
- 修复 Approval 类型缺少 updated_at 字段
