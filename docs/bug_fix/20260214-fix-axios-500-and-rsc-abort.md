# Axios 500 错误与 Next.js RSC 请求失败修复记录

## 问题描述
- **现象**：
  1. 用户日志显示大量 Next.js RSC 请求 `net::ERR_ABORTED`。
  2. Axios 请求后端 `/api/v1/contents` 报 500 Internal Server Error。
  3. 前端调用 `/health/report` 报 404 Not Found。
- **复现步骤**：
  1. 访问前端页面，触发服务端数据获取。
  2. 访问 `/api/v1/contents` 接口。
- **影响范围**：
  - 前端页面加载失败（空白或报错）。
  - 内容列表无法加载。
  - 健康检查功能不可用。

## 根因分析
- **直接原因**：
  1. **RSC Abort**: 前端在服务端渲染时，`axios` 使用默认的相对路径 `/api/v1`，导致请求失败（服务端无法解析相对路径）。
  2. **Axios 500**: 后端 SQLAlchemy 在异步模式下，`ContentItem` 模型访问了延迟加载的 `validation_result` 属性，触发 `MissingGreenlet` 错误。
  3. **404**: 前端 API 路径 `/health/report` 与后端定义的 `/health/report/latest` 不匹配。
- **根本原因**：
  1. 前端 `api.ts` 配置未考虑服务端环境（SSR/RSC）的 Base URL 需求。
  2. 后端查询未预加载关联数据（N+1 问题在异步下的表现）。
  3. 前后端 API 路径定义不一致。
- **相关代码**：
  - `frontend/src/lib/api.ts`
  - `backend/app/routers/contents.py`

## 修复方案
- **修复思路**：
  1. 修改前端 `api.ts`，区分服务端和客户端环境，服务端使用 `http://127.0.0.1:8000/api/v1`。
  2. 修改后端 `contents.py`，使用 `selectinload` 预加载 `validation_result`。
  3. 修正前端 `healthApi.getReport` 路径。
- **改动文件**：
  - `frontend/src/lib/api.ts`
  - `backend/app/routers/contents.py`

## 验证结果
- [x] 原问题已解决：curl 测试 `/api/v1/contents` 返回 200 OK，包含 `validation_result`。
- [x] 回归测试通过：前端服务正常启动，后端无报错。
- [x] 设计一致性确认：符合异步加载和 API 代理设计。

## 提交信息
fix(api): 修复服务端 BaseURL 配置及后端异步加载错误
