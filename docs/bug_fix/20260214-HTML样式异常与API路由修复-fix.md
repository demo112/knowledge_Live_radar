# 20260214-HTML样式异常与API路由修复-fix.md

## 问题描述
- **现象**：HTML 页面样式异常，控制台出现 23 条日志（包括 `net::ERR_ABORTED` 和 `404` 错误）。
- **复现步骤**：访问 `/zh/contents` 页面，执行一键清洗操作。
- **影响范围**：前端内容管理页面、API 调用、i18n 路由。

## 设计锚定
- **所属规格**：clean-and-summary, i18n
- **原设计意图**：
  - 批量操作 API 路径应为 `/api/v1/contents/batch/*`。
  - 使用 `next-intl` 处理多语言路由。
- **当前偏离**：
  - 后端路由前缀为 `/content-management`，与设计不符。
  - 前端 API 调用路径与后端不匹配，导致 `net::ERR_ABORTED`。
  - Next.js 16 中 `middleware.ts` 命名冲突（应使用 `proxy.ts` 或更新配置）。

## 根因分析
- **直接原因**：前端调用的 API 路径在后端不存在，且 Next.js 16 编译器对过时的中间件配置报错。
- **根本原因**：代码实现偏离了 `design.md` 中的 API 契约，且未及时跟进 Next.js 16 的配置变更。
- **相关代码**：`backend/app/routers/content_management.py`, `frontend/src/lib/api.ts`, `frontend/src/proxy.ts`

## 修复方案
- **修复思路**：
  1. 将后端路由前缀和路径对齐到设计文档。
  2. 统一前后端 API 响应格式，确保包含 `success: true`。
  3. 修复 Next.js i18n 路由配置。
- **改动文件**：
  - [content_management.py](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/backend/app/routers/content_management.py)
  - [main.py](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/backend/app/main.py)
  - [api.ts](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/frontend/src/lib/api.ts)
  - [proxy.ts](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/frontend/src/proxy.ts)

## 验证结果
- [x] 原问题已解决：`net::ERR_ABORTED` 错误消失，API 调用正常。
- [x] 回归测试通过：后端单元测试通过，前端 `npm run build` 成功。
- [x] 设计一致性确认：API 路径与 `design.md` 保持一致。

## 文档同步
- [x] design.md：无需更新，代码已对齐设计。
- [ ] api-contract.md：无需更新。

## 提交信息
fix(api): 修复内容管理批量操作路由不匹配及 i18n 配置问题
