# 20260214-fix-tabs-build-error 修复记录

## 问题描述
- **现象**：前端构建失败，报错 `Module not found: Can't resolve '@/components/ui/tabs'`。
- **复现步骤**：运行 `npm run build` 或 `npm run dev`。
- **影响范围**：前端应用无法启动和构建。

## 根因分析
- **直接原因**：`frontend/src/components/ui/tabs.tsx` 文件缺失，但在 `InputBox.tsx` 中被引用。
- **关联原因**：
  - `Textarea` 组件缺失。
  - `Card` 组件缺少 `CardFooter` 和 `CardDescription` 导出。
  - `use-toast` hook 缺失。
  - `AIReasoningDisplay` 组件缺少 `steps` 属性定义。
  - `LanguageSwitcher` 和 `NodeActions` 中 `Select` 组件的使用方式与新版 Radix UI 封装不兼容（使用了 `onChange` 而非 `onValueChange`）。

## 修复方案
- **创建缺失组件**：
  - `frontend/src/components/ui/tabs.tsx`
  - `frontend/src/components/ui/textarea.tsx`
  - `frontend/src/components/ui/toast.tsx`
  - `frontend/src/components/ui/toaster.tsx`
  - `frontend/src/hooks/use-toast.ts`
- **更新现有组件**：
  - `frontend/src/components/ui/card.tsx`：添加 missing exports。
  - `frontend/src/components/ui/select.tsx`：完善 Radix UI 封装。
  - `frontend/src/components/ai/AIReasoningDisplay.tsx`：修复接口定义。
- **修复类型错误**：
  - `frontend/src/components/LanguageSwitcher.tsx`：迁移到 `Select` 的 `onValueChange` API。
  - `frontend/src/components/pyramid/NodeActions.tsx`：迁移到 `Select` 的 `onValueChange` API。

## 验证结果
- [x] `pnpm tsc --noEmit` 通过（无类型错误）。
- [x] `npm run build` 通过（构建成功）。

## 提交信息
fix(frontend): 修复 tabs 组件缺失及相关构建错误

- 新增 tabs, textarea, toast 等缺失 UI 组件
- 修复 LanguageSwitcher 和 NodeActions 中的 Select 组件类型错误
- 完善 Card 和 AIReasoningDisplay 组件定义
- 验证通过前端构建
