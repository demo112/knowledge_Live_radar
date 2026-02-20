# Tasks

- [x] Task 1: Firecrawl 基础设施搭建 (Docker)
  - [x] SubTask 1.1: 创建/修改 `docker-compose.yml`，增加 Firecrawl 及其依赖服务 (Redis, Playwright, API, Worker)
  - [ ] SubTask 1.2: 验证 Firecrawl 服务是否启动成功 (访问 http://localhost:3002/test)
  - [x] SubTask 1.3: 更新 `docs/deployment.md`，记录 Firecrawl 服务的依赖

- [x] Task 2: 后端集成 (Python)
  - [x] SubTask 2.1: 在 `backend/requirements.txt` 中添加 `firecrawl-py` 依赖
  - [x] SubTask 2.2: 在 `backend/app/core/config.py` 和 `.env` 中添加 `FIRECRAWL_API_URL` 和 `FIRECRAWL_API_KEY` 配置
  - [x] SubTask 2.3: 创建 `backend/app/services/fetchers/firecrawl_fetcher.py`，实现 `FirecrawlFetcher` 类
  - [x] SubTask 2.4: 修改 `backend/app/services/fetchers/__init__.py` 和 `backend/app/services/crawl_engine.py`，注册并使用 `FirecrawlFetcher`

- [ ] Task 3: 验证与调试
  - [x] SubTask 3.1: 编写集成测试 `backend/tests/integration/test_firecrawl_fetcher.py`，测试抓取功能 (Mock passed)
  - [ ] SubTask 3.2: 运行测试，确保 Firecrawl 能正常抓取并返回 Markdown 数据 (Real service test pending)
  - [ ] SubTask 3.3: (Optional) 在前端触发一次抓取任务，观察全链路运行情况
  - [ ] SubTask 3.4: 使用 `backend/scripts/verify_firecrawl.py` 进行手动验证

# Task Dependencies
- [Task 2] depends on [Task 1] (Backend needs Firecrawl service running)
- [Task 3] depends on [Task 2] (Validation needs code implementation)
