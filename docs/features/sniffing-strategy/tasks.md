# Tasks: 嗅探优先的爬取策略

## Todo List

- [x] Task 1: 创建 `RequestUtils` 模块 <!-- id: 1 -->
  - [x] 实现 `backend/app/services/fetchers/request_utils.py`
  - [x] 包含 `UserAgentPool`
  - [x] 包含 `smart_request` 函数（带重试、随机延迟、429处理）

- [x] Task 2: 改造 `RSSFetcher` <!-- id: 2 -->
  - [x] 移除硬编码 Headers
  - [x] 替换 `httpx.AsyncClient` 调用为 `smart_request`
  - [x] 增加对 `RateLimitException` 的处理

- [x] Task 3: 改造 `WebFetcher` <!-- id: 3 -->
  - [x] 移除硬编码 Headers
  - [x] 替换 `httpx.AsyncClient` 调用为 `smart_request`
  - [x] 优化 `validate_source` 方法使用 HEAD 请求

- [x] Task 4: 调整 `CrawlManager` <!-- id: 4 -->
  - [x] 降低默认并发度
  - [x] (可选) 实现简单的域名锁

## Dependencies

- 无外部依赖

## Notes

- 确保 `smart_request` 中处理好 SSL 错误和超时
- 429 错误应抛出特定异常，以便上层捕获
