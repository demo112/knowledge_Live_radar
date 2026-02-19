# Requirements: Firecrawl 私有化集成

## Overview

目前 `crawl_engine.py` 仅为框架，无法处理动态网页且缺乏高质量的 Markdown 提取能力。为了支持 AI Radar 的核心“知识聚合”能力，我们将引入 **Firecrawl (Self-hosted)** 作为核心网页抓取引擎。私有化部署可以直接获得高质量的 LLM-ready 数据，同时保证数据隐私完全可控，且无外部 API 调用成本。

## User Stories

### Story 1: 部署本地 Firecrawl 服务

As a 系统管理员, I want 在本地 Docker 环境中运行 Firecrawl 服务, So that 系统可以调用本地 API 进行网页抓取，无需依赖外部 SaaS 服务。

**Acceptance Criteria:**

- [ ] AC1: Docker Compose 服务编排
  - **Given**: 项目根目录下的 `docker-compose.yml`
  - **When**: 运行 `docker-compose up -d`
  - **Then**: 
    - 启动 `firecrawl-api` 服务 (Port 3002)
    - 启动 `firecrawl-worker` 服务
    - 启动 `playwright-service` 服务
    - 启动依赖的 Redis 服务

- [ ] AC2: 服务健康检查
  - **Given**: 所有容器已启动
  - **When**: 访问 `http://localhost:3002/test` (或对应的健康检查端点)
  - **Then**: 返回状态码 200 或 "Hello, world!"

### Story 2: 集成 FirecrawlFetcher

As a 抓取引擎, I want 调用本地 Firecrawl 服务来处理 WEB 类型的信源, So that 我可以获得高质量的 Markdown 格式内容。

**Acceptance Criteria:**

- [ ] AC1: 封装 Firecrawl SDK
  - **Given**: 系统配置了 `FIRECRAWL_API_URL` 指向本地服务
  - **When**: `CrawlEngine` 调度抓取任务
  - **Then**: `FirecrawlFetcher` 使用 Python SDK (或 HTTP 请求) 调用本地 API

- [ ] AC2: 处理抓取结果
  - **Given**: Firecrawl 返回了抓取结果
  - **When**: Fetcher 解析响应
  - **Then**: 
    - 提取 `content.markdown` 作为主要内容
    - 提取 `metadata` (title, description, og:image)
    - 能够正确处理并记录抓取失败的情况 (Error Logging)

## Constraints

- **资源消耗**: Firecrawl (特别是 Playwright) 消耗较多 CPU 和内存，需确保开发机和服务器有足够资源。
- **环境隔离**: 必须通过 Docker 网络或宿主机端口正确配置服务间通信。
- **API Key**: 即使是 Self-hosted 版本，SDK 可能仍要求传入 API Key (可设置为空字符串或任意值)。

## Dependencies

- **Docker & Docker Compose**: 必须安装。
- **Python Library**: `firecrawl-py`。
- **Redis**: 用于任务队列。

## Metadata

- 规模: 中
- 涉及模块: `crawl_engine`, `docker-compose`
- 涉及端: Backend, DevOps
- 创建时间: 2026-02-19
- 状态: 已确认
