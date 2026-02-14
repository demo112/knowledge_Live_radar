# Design: 嗅探优先的爬取策略

## 1. 架构调整

在现有的 `CrawlEngine` 和 `Fetcher` 之间引入 `RequestStrategy` 层，或者直接增强 `Fetcher` 的基础能力。为了保持简单，我们将直接在 `BaseFetcher` 或工具类中实现拟人化逻辑。

### 核心模块变更

1.  **`app/services/fetchers/base.py` (新增/修改)**
    *   增加 `UserAgentPool`: 维护一个常见浏览器 User-Agent 列表。
    *   增加 `RateLimiter`: 单域名速率限制器。
    *   增加 `make_request` 方法：封装 `httpx` 调用，自动注入 Headers 和执行延时。

2.  **`app/services/crawl_engine.py`**
    *   修改 `crawl_source` 方法，在调用 Fetcher 前后增加随机等待。
    *   增加对 `429/403` 异常的捕获和特殊处理（抛出 `RateLimitException`）。

3.  **`app/services/scheduler/crawl_manager.py`**
    *   调整并发度 `self.concurrency`，建议默认降为 2-3。
    *   增加单域名锁（Domain Lock），确保同一时间对同一域名只有一个 Worker 在工作。

## 2. 详细设计

### 2.1 拟人化请求头 (Humanized Headers)

创建一个工具类 `RequestUtils`：

```python
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
    # ... 更多
]

def get_random_headers(referer: str = None) -> dict:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,...",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer
    return headers
```

### 2.2 随机延迟 (Random Delay)

在每次请求前引入随机延迟。

```python
import asyncio
import random

async def random_sleep(min_seconds=2, max_seconds=5):
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Sleeping for {delay:.2f}s for sniffing...")
    await asyncio.sleep(delay)
```

### 2.3 智能避让 (Smart Backoff)

当捕获到 `httpx.HTTPStatusError` 且状态码为 429 或 403 时：
1.  记录日志。
2.  暂时“冷却”该 Source（更新 `next_crawl_time` 到 2-4 小时后）。
3.  不标记为永久 `FAILED`，而是标记为 `SKIPPED` 或 `COOLDOWN`。

### 2.4 嗅探逻辑 (Sniffing Logic)

对于 RSS 源：
*   保持现有逻辑，但增加 UA 和 Delay。RSS 本身就是嗅探机制。

对于网页源：
*   **Phase 1 (Sniff)**: 请求入口 URL。计算内容哈希或检查 `Last-Modified`。
*   **Phase 2 (Decide)**: 如果哈希变化或有新链接，才进行后续处理。
*   *注：当前版本先实现通用的“慢速拟人请求”，暂不实现复杂的哈希比对，利用现有的去重逻辑即可。核心是“慢”和“伪装”。*

## 3. 数据库变更

无。复用现有的 `InformationSource` 表结构。

## 4. 接口变更

无。内部逻辑调整。

## 5. 验证计划

1.  **单元测试**: 验证 Headers 生成器是否随机。
2.  **集成测试**: 启动爬虫，观察日志中的请求间隔和 User-Agent。
3.  **E2E**: 针对一个测试源（如 httpbin.org/headers）验证请求头。
