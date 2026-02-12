# 20260212-fix-404-handling-fix.md

## 问题描述
- **现象**：浏览器控制台显示大量 404 错误日志，且部分删除操作在对象已不存在时提示"失败"，给用户造成困扰。
- **复现步骤**：
  1. 访问不存在的金字塔详情页。
  2. 在列表页尝试删除一个已经被删除（或不存在）的金字塔/信息源。
- **影响范围**：金字塔详情页、金字塔列表页、信息源列表页、白名单管理、审批列表。

## 设计锚定
- **所属规格**：manual-crud
- **原设计意图**：API 调用失败时应显示友好提示，删除操作应确保从列表中移除。
- **当前偏离**：
  - 详情页 404 时控制台报错，虽然 UI 显示"未找到"，但日志不友好。
  - 删除操作 404 时提示"删除失败"，实际上对象已消失，应视为成功（幂等性）。

## 根因分析
- **直接原因**：Axios 默认将 404 视为异常抛出，代码 catch 块中统一使用 `console.error` 记录所有异常。
- **根本原因**：前端缺乏对 404 (Not Found) 状态的特定处理逻辑，未区分"系统错误"和"资源不存在"。
- **相关代码**：
  - `frontend/src/app/(dashboard)/pyramid/[id]/page.tsx`
  - `frontend/src/app/(dashboard)/pyramid/page.tsx`
  - `frontend/src/app/(dashboard)/sources/page.tsx`
  - `frontend/src/app/(dashboard)/sources/whitelist/page.tsx`
  - `frontend/src/components/approval/ApprovalList.tsx`

## 修复方案
- **修复思路**：在 catch 块中检查 `error.response.status === 404`。如果是 404，则抑制错误日志，并执行相应的"资源不存在"逻辑（如刷新列表、置空状态）。
- **改动文件**：上述 5 个文件。

## 关联组件
| 组件 | 文件路径 | 是否同步修复 |
|------|----------|--------------|
| PyramidDetailPage | `frontend/src/app/(dashboard)/pyramid/[id]/page.tsx` | ✅ |
| PyramidListPage | `frontend/src/app/(dashboard)/pyramid/page.tsx` | ✅ |
| SourcesPage | `frontend/src/app/(dashboard)/sources/page.tsx` | ✅ |
| WhitelistTab | `frontend/src/app/(dashboard)/sources/whitelist/page.tsx` | ✅ |
| ApprovalList | `frontend/src/components/approval/ApprovalList.tsx` | ✅ |

## 验证结果
- [x] 原问题已解决（逻辑审查确认）
- [x] 回归测试通过（`npm run build` pass）
- [x] 设计一致性确认

## 文档同步
- [ ] design.md：无需更新（属于实现细节优化）

## 提交信息
fix(frontend): 优化 404 错误处理逻辑，避免不必要的控制台报错
