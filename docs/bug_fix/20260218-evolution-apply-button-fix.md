# Evolution Apply 按钮无法点击修复记录

## 问题描述
- **现象**：用户反馈 Evolution 面板中的 "同意" 按钮无法点击，且按钮文本显示为 `evolution.apply`。后续发现控制台报错 `translateFn`。
- **复现步骤**：
  1. 进入金字塔详情页。
  2. 触发结构分析。
  3. 生成建议后，尝试点击 "同意" (Apply) 按钮。
- **影响范围**：金字塔进化建议应用功能。

## 设计锚定
- **所属规格**：`pyramid-evolution`
- **原设计意图**：`AC3: 结构调整建议`，用户应能一键应用 AI 生成的结构调整建议。
- **当前偏离**：
  1. 翻译键值大小写不一致导致文本显示为键名。
  2. 缺少加载状态反馈，导致用户可能以为无法点击或重复点击。
  3. 组件缺少 `'use client'` 声明，可能导致交互失效。
  4. 后端生成的 `action_type` (如 `move_node`, `fix_drift`) 在前端翻译文件中缺失，导致页面崩溃。

## 根因分析
- **直接原因**：
  1. `zh.json` / `en.json` 中使用 `evolution` (小写)，而 `EvolutionPanel.tsx` 中使用 `useTranslations('Evolution')`。改为 `Evolution` (大写)。
  2. 按钮在点击后没有立即给出反馈（loading 状态）。
  3. `EvolutionPanel.tsx` 未显式声明 `'use client'`。
  4. `AISuggestion` 的 `action_type` 包含了 `move_node` 和 `fix_drift`，但前端翻译文件中未定义这些键，导致 `next-intl` 抛错。

## 修复方案
- **修复思路**：
  1. 统一翻译键名为 `Evolution` (大写)。
  2. 增加 `applyingId` 状态，用于跟踪正在应用的建议，并展示 Loading 状态。
  3. 添加 `'use client'` 声明。
  4. 补全 `zh.json` 和 `en.json` 中的翻译键 (`move_node`, `fix_drift`)。
  5. 在 `EvolutionPanel.tsx` 中添加错误边界 (`try-catch`)，防止因翻译缺失导致组件崩溃。
- **改动文件**：
  - `frontend/src/components/pyramid/EvolutionPanel.tsx`
  - `frontend/messages/zh.json`
  - `frontend/messages/en.json`

## 验证结果
- [x] 原问题已解决：翻译显示正常，点击有 Loading 反馈。
- [x] 翻译报错已修复：补充了缺失的 key，并添加了 fallback。
- [x] 回归测试通过：编译通过。
- [x] 设计一致性确认：符合 `design.md` 中的 AC3 要求。

## 文档同步
- [ ] design.md：无需更新。
- [ ] api-contract.md：无需更新。

## 提交信息
fix(pyramid): 修复进化建议翻译缺失导致的页面错误及按钮交互问题
