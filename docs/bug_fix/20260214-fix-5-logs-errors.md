# 5 条日志错误修复记录

## 问题描述
- **现象**：
  1. 浏览器控制台出现 3 个 `net::ERR_ABORTED` 导航错误。
  2. 国际化报错 `MISSING_MESSAGE: Could not resolve Pyramid.Detail.NodeActions`。
  3. 批量摘要接口 `/api/v1/contents/batch/summarize` 在输入无效 UUID 时返回 500 错误。
- **复现步骤**：
  1. 在金字塔详情页右键点击节点，触发拆分/合并/关联对话框，控制台报错 i18n 路径未找到。
  2. 使用 `curl` 或前端调用批量摘要接口，传入非 UUID 字符串，后端报错 500。
  3. 切换页面或点击侧边栏链接时，部分请求被中止。
- **影响范围**：金字塔操作功能、内容库批量管理、系统整体导航。

## 设计锚定
- **所属规格**：`clean-and-summary`, `i18n`
- **原设计意图**：
  - 批量摘要接口应验证输入合法性并异步处理任务。
  - 国际化文本应按模块组织在 `messages/zh.json` 中。
- **当前偏离**：
  - 代码中引用的 i18n 路径与资源文件结构不一致。
  - 后端接口缺少 Pydantic 类型校验。
  - Middleware 文件命名不规范导致 Next.js 无法自动识别。

## 根因分析
- **直接原因**：
  - `NodeActions.tsx` 错误使用了 `Pyramid.Detail.NodeActions` 路径。
  - 后端 schema 使用 `str` 而非 `uuid.UUID` 导致转换失败未被捕获。
  - `middleware.ts` 被重命名为 `proxy.ts`，Next.js 未能正确应用国际化路由中间件。
- **根本原因**：代码实现与设计规范同步不及时，缺乏类型严谨性。

## 修复方案
- **修复思路**：
  1. 修正前端 i18n 引用路径。
  2. 强化后端参数类型校验。
  3. 规范 Next.js Middleware 命名。
  4. 同步更新 E2E 测试 POM 以适配 UI 变更。
- **改动文件**：
  - `frontend/src/components/pyramid/NodeActions.tsx`
  - `backend/app/schemas/content_management.py`
  - `backend/app/services/content_management_service.py`
  - `frontend/src/middleware.ts` (重命名自 `proxy.ts`)
  - `e2e/pages/pyramid-detail.page.ts`
  - `e2e/tests/pyramid/snapshot.spec.ts`

## 验证结果
- [x] 原问题已解决：i18n 报错消失，API 返回 422 校验错误。
- [x] 回归测试通过：Playwright `snapshot.spec.ts` 运行通过。
- [x] 设计一致性确认：符合 `clean-and-summary` 和 `i18n` 设计文档。

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(pyramid): 修复国际化路径、批量摘要校验及导航错误
