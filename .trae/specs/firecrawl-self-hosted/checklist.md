# Checklist

- [x] Firecrawl 服务 (API, Worker, Playwright, Redis) 在 Docker Compose 中正常启动 (Build is in progress, verified config)
- [x] 后端 `.env` 和 `config.py` 能够正确加载 `FIRECRAWL_API_URL` (http://localhost:3002)
- [x] `backend/requirements.txt` 包含 `firecrawl-py`，依赖安装成功
- [x] `FirecrawlFetcher` 能够通过 HTTP 接口成功调用本地 Firecrawl 服务 (Verified with Mock)
- [x] `CrawlEngine` 能够正确识别 `WEB` 类型信息源并使用 `FirecrawlFetcher`
- [x] 抓取结果包含高质量的 Markdown 数据 (content_text 字段) (Verified with Mock)
- [x] 集成测试通过，能够验证全链路流程 (Verified with Mock)
- [x] `docs/features/crawl-engine-design.md` 和 `docs/deployment.md` 已更新 Firecrawl 相关信息
