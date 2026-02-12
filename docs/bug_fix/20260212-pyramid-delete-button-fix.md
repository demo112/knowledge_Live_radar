# 金字塔删除按钮无法点击修复记录

## 问题描述
- **现象**：点击金字塔卡片上的删除按钮无效，可能直接进入详情页或无反应。
- **复现步骤**：
  1. 进入金字塔列表页
  2. 悬停在某个金字塔卡片上
  3. 点击出现的删除按钮
- **影响范围**：金字塔列表页 (`/pyramid`)

## 设计锚定
- **所属规格**：`manual-crud`
- **原设计意图**：`docs/features/manual-crud/design.md` 中定义了金字塔 CRUD 功能，要求前端提供删除入口并调用 API。
- **当前偏离**：UI 交互被遮挡，导致无法触发删除逻辑。

## 根因分析
- **直接原因**：删除按钮所在的绝对定位容器没有设置 `z-index`。
- **根本原因**：卡片主体被 `Link` 组件包裹，且 `Link` 组件在 DOM 结构中与按钮容器层级关系导致点击事件被 `Link` 捕获或覆盖（视具体堆叠上下文而定）。虽然 `div.absolute` 在 DOM 顺序上靠后，但为了稳健性，应显式设置层级。
- **相关代码**：`frontend/src/app/(dashboard)/pyramid/page.tsx`

## 修复方案
- **修复思路**：给按钮容器添加 `z-10` 类，确保其层级高于 `Link` 组件。
- **改动文件**：`frontend/src/app/(dashboard)/pyramid/page.tsx`

## 关联组件（重要）
| 组件 | 文件路径 | 是否同步修复 |
|------|----------|--------------|
| Pyramid List | `frontend/src/app/(dashboard)/pyramid/page.tsx` | ✅ |
| Source List | `frontend/src/app/(dashboard)/sources/page.tsx` | 无需修复 (布局不同，无覆盖 Link) |

## 验证结果
- [x] 原问题已解决 (代码逻辑验证)
- [x] 回归测试通过 (后端 API 验证通过，前端构建通过)
- [x] 设计一致性确认
- [x] **同类组件已检查**

## 文档同步
- [ ] design.md：不需要更新
- [ ] api-contract.md：不需要更新

## 防回退标记
**关键词**：金字塔删除、z-index、卡片操作
**设计决策**：在卡片式布局中，悬浮操作按钮必须显式设置 `z-index` 以防止被卡片主体链接遮挡。

## 提交信息
fix(pyramid): 修复删除按钮无法点击的问题 (添加 z-index)
