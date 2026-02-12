# 变更历史页面汉化修复记录

## 问题描述
- **现象**：变更历史 (Change History) 页面及其相关组件显示为英文。
- **复现步骤**：访问 `/history` 页面。
- **影响范围**：变更历史页面、时间轴组件、详情弹窗、回滚确认弹窗。

## 设计锚定
- **所属规格**：Requirement 12 (变更历史) & Requirement 26 (变更历史界面)
- **原设计意图**：系统应提供变更历史查询和回滚功能。设计文档未明确指定语言，但作为中文系统，界面应为中文。
- **当前偏离**：界面文本硬编码为英文。

## 根因分析
- **直接原因**：前端代码 (`page.tsx`, `ChangeTimeline.tsx` 等) 中的文本硬编码为英文。
- **根本原因**：开发初期未考虑国际化或默认使用了英文开发。
- **相关代码**：`frontend/src/app/(dashboard)/history/page.tsx`

## 修复方案
- **修复思路**：
  1. 将硬编码的英文文本替换为中文。
  2. 提取常量映射 (`CHANGE_STATUS_MAP`, `CHANGE_TYPE_MAP`) 到 `frontend/src/lib/constants.ts` 以复用和统一术语。
  3. 将 `ChangeItem` 接口移动到 `frontend/src/lib/types.ts` 以消除重复定义。
- **改动文件**：
  - `frontend/src/lib/constants.ts` (新增)
  - `frontend/src/lib/types.ts` (修改)
  - `frontend/src/app/(dashboard)/history/page.tsx` (修改)
  - `frontend/src/components/history/ChangeTimeline.tsx` (修改)
  - `frontend/src/components/history/ChangeDetail.tsx` (修改)
  - `frontend/src/components/history/RollbackDialog.tsx` (修改)

## 关联组件
| 组件 | 文件路径 | 是否同步修复 |
|------|----------|--------------|
| ChangeTimeline | `frontend/src/components/history/ChangeTimeline.tsx` | ✅ |
| ChangeDetail | `frontend/src/components/history/ChangeDetail.tsx` | ✅ |
| RollbackDialog | `frontend/src/components/history/RollbackDialog.tsx` | ✅ |

## 验证结果
- [x] 原问题已解决（代码已汉化）
- [x] 回归测试通过（`pnpm build` passed）
- [x] 设计一致性确认

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 防回退标记
**关键词**：汉化、变更历史、History Page
**设计决策**：统一使用 `constants.ts` 管理状态和类型的中文映射。

## 提交信息
fix(frontend): 汉化变更历史页面及相关组件
