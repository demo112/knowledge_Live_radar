# 前端连接后端失败 (CORS) 修复记录

## 问题描述
- **现象**：前端浏览器控制台出现大量 `AxiosError: Network Error` 和 `net::ERR_FAILED`，无法连接后端 API。
- **复现步骤**：
  1. 启动后端 (port 8000)
  2. 启动前端 (Next.js 自动 fallback 到 port 3001)
  3. 访问前端页面
- **影响范围**：所有前端页面无法加载数据。

## 设计锚定
- **所属规格**：API 通信
- **原设计意图**：前后端分离，通过 CORS 允许跨域访问。
- **当前偏离**：后端 CORS 白名单仅包含 `localhost:3000`，未覆盖 Next.js 自动 fallback 的 `3001` 端口或其他开发端口。

## 根因分析
- **直接原因**：浏览器拦截了来自 `http://localhost:3001` 的跨域请求，因为后端未返回允许的 `Access-Control-Allow-Origin`。
- **根本原因**：后端 `backend/app/main.py` 中的 CORS `origins` 列表硬编码了端口，缺乏灵活性。
- **相关代码**：`backend/app/main.py:86`

## 修复方案
- **修复思路**：在开发环境中放宽 localhost 的 CORS 限制，使用正则匹配所有 localhost 端口。
- **改动文件**：
  - `backend/app/main.py`

## 验证结果
- [x] 原问题已解决：curl 验证 `Origin: http://localhost:3001` 返回 200 OK 及正确 Header。
- [x] 回归测试通过：不影响原 3000 端口访问。
- [x] 设计一致性确认：符合开发环境便利性原则。

## 提交信息
fix(config): 允许所有 localhost 端口跨域访问以支持 Next.js 动态端口
