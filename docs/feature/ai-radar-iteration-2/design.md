# 设计文档 - 迭代 2：信息抓取

## 概述

本设计文档描述 AI Radar 系统迭代 2 的技术实现方案。迭代 2 的目标是实现动态信息源管理和内容抓取校验机制。

## 架构设计

### 抓取系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        抓取调度器                                │
│                    (Crawl_Scheduler)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │  RSS_Fetcher  │ │  API_Fetcher  │ │  Web_Fetcher  │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            └─────────────────┼─────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        去重服务                                  │
│                  (Deduplication_Service)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        校验流水线                                │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Hard_Validator │  Soft_Validator │    Cross_Validator          │
│   (规则校验)    │   (AI 校验)     │     (交叉验证)              │
└─────────────────┴────────┬────────┴─────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        内容处理                                  │
├─────────────────────────┬───────────────────────────────────────┤
│   AI_Summary_Service    │      Content_Classifier               │
│     (摘要生成)          │        (内容分类)                     │
└─────────────────────────┴───────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储                                  │
│                    (Content_Items)                              │
└─────────────────────────────────────────────────────────────────┘
```

### 信息源生命周期状态机

```
                    ┌──────────────┐
                    │  discovered  │ ← 新创建
                    └──────┬───────┘
                           │ 首次抓取成功
                           ▼
                    ┌──────────────┐
                    │   verified   │
                    └──────┬───────┘
                           │ 连续3次成功
                           ▼
              ┌───────────────────────────┐
              │          active           │ ←──────────────┐
              └─────────────┬─────────────┘                │
                            │ 失败率>30%                   │ 恢复正常
                            ▼                              │
              ┌───────────────────────────┐                │
              │        monitoring         │ ───────────────┘
              └─────────────┬─────────────┘
                            │ 连续7天异常
                            ▼
              ┌───────────────────────────┐
              │        adjusting          │ → 生成 Change_Proposal
              └─────────────┬─────────────┘
                            │ 人工判定无效
                            ▼
              ┌───────────────────────────┐
              │         retired           │ → 停止抓取
              └───────────────────────────┘
```


## 目录结构（新增）

```
backend/
├── app/
│   ├── services/
│   │   ├── fetcher/                 # 抓取引擎
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 抓取器基类
│   │   │   ├── rss_fetcher.py       # RSS 抓取器
│   │   │   ├── api_fetcher.py       # API 抓取器
│   │   │   └── web_fetcher.py       # 网页抓取器
│   │   ├── validator/               # 校验引擎
│   │   │   ├── __init__.py
│   │   │   ├── hard_validator.py    # 硬性校验
│   │   │   ├── soft_validator.py    # 软性校验（AI）
│   │   │   └── cross_validator.py   # 交叉验证
│   │   ├── processor/               # 内容处理
│   │   │   ├── __init__.py
│   │   │   ├── deduplication.py     # 去重服务
│   │   │   ├── summarizer.py        # 摘要生成
│   │   │   └── classifier.py        # 内容分类
│   │   ├── lifecycle/               # 生命周期管理
│   │   │   ├── __init__.py
│   │   │   ├── source_lifecycle.py  # 信息源生命周期
│   │   │   └── health_monitor.py    # 健康监测
│   │   ├── discovery/               # 信息源发现
│   │   │   ├── __init__.py
│   │   │   └── source_discovery.py  # 自动发现
│   │   └── ai/                      # AI 服务
│   │       ├── __init__.py
│   │       ├── siliconflow_client.py # 硅基流动客户端
│   │       └── prompts.py           # Prompt 模板
│   ├── scheduler/                   # 调度器
│   │   ├── __init__.py
│   │   └── crawl_scheduler.py       # 抓取调度
│   └── models/
│       ├── crawl_job.py             # 抓取任务记录
│       └── domain_whitelist.py      # 域名白名单
```

## 数据模型（新增）

### 抓取任务记录

```python
class CrawlJob(Base):
    __tablename__ = "crawl_jobs"
    
    id: str                    # UUID
    source_id: str             # 信息源 ID
    status: str                # running/success/failed
    started_at: datetime       # 开始时间
    ended_at: datetime | None  # 结束时间
    items_fetched: int         # 抓取条目数
    items_new: int             # 新增条目数
    items_duplicate: int       # 重复条目数
    error_message: str | None  # 错误信息
    response_time_ms: int | None  # 响应时间
```

### 域名白名单

```python
class DomainWhitelist(Base):
    __tablename__ = "domain_whitelist"
    
    id: str                    # UUID
    domain: str                # 域名（支持通配符）
    credibility: str           # authoritative/normal/unverified
    reason: str                # 添加原因
    created_at: datetime
    is_deleted: bool
```

### 内容校验结果

```python
class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id: str                    # UUID
    content_id: str            # 内容 ID
    hard_validation: dict      # 硬性校验结果 JSON
    soft_validation: dict      # 软性校验结果 JSON
    cross_validation: dict     # 交叉验证结果 JSON
    overall_status: str        # passed/failed/pending
    quality_score: int         # 综合质量分数 0-100
    created_at: datetime
```

### 发现的域名记录

```python
class DiscoveredDomain(Base):
    __tablename__ = "discovered_domains"
    
    id: str                    # UUID
    domain: str                # 域名
    occurrence_count: int      # 出现次数
    first_seen_at: datetime    # 首次发现时间
    last_seen_at: datetime     # 最后发现时间
    evaluation_status: str     # pending/evaluated/proposed/rejected
    has_rss: bool | None       # 是否有 RSS
    proposal_id: str | None    # 关联的提案 ID
```


## 组件接口设计

### 抓取器基类

```python
# services/fetcher/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class FetchResult:
    success: bool
    items: list[dict]          # 抓取到的条目
    error_message: str | None
    response_time_ms: int

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, source: InformationSource) -> FetchResult:
        """执行抓取任务"""
        pass
    
    @abstractmethod
    def validate_config(self, config: dict) -> tuple[bool, str]:
        """验证信息源配置"""
        pass
```

### RSS 抓取器

```python
# services/fetcher/rss_fetcher.py
class RSSFetcher(BaseFetcher):
    async def fetch(self, source: InformationSource) -> FetchResult:
        """
        抓取 RSS/Atom 源
        config 结构:
        {
            "url": "https://example.com/feed.xml",
            "timeout": 30,
            "user_agent": "AI-Radar/1.0"
        }
        """
        pass
```

### API 抓取器

```python
# services/fetcher/api_fetcher.py
class APIFetcher(BaseFetcher):
    async def fetch(self, source: InformationSource) -> FetchResult:
        """
        抓取 API 数据
        config 结构:
        {
            "url": "https://api.example.com/data",
            "method": "GET",
            "headers": {"Authorization": "Bearer xxx"},
            "params": {"page": 1},
            "auth_type": "bearer",  # bearer/api_key/basic
            "response_path": "$.data[*]",  # JSONPath
            "field_mapping": {
                "title": "$.name",
                "url": "$.link",
                "published_at": "$.created_at"
            },
            "pagination": {
                "type": "page",  # page/cursor/offset
                "param": "page",
                "max_pages": 5
            }
        }
        """
        pass
```

### 网页抓取器

```python
# services/fetcher/web_fetcher.py
class WebFetcher(BaseFetcher):
    async def fetch(self, source: InformationSource) -> FetchResult:
        """
        抓取网页内容
        config 结构:
        {
            "url": "https://blog.example.com",
            "list_selector": "article.post",  # CSS 选择器
            "item_selectors": {
                "title": "h2.title",
                "url": "a.link@href",
                "summary": "p.excerpt",
                "published_at": "time@datetime"
            },
            "detail_page": true,  # 是否抓取详情页
            "detail_selectors": {
                "content": "div.content"
            },
            "rate_limit": 1.0  # 请求间隔（秒）
        }
        """
        pass
```


### 校验器接口

```python
# services/validator/hard_validator.py
@dataclass
class HardValidationResult:
    passed: bool
    checks: list[dict]  # [{"rule": "url_format", "passed": True, "message": ""}]

class HardValidator:
    async def validate(self, content: dict) -> HardValidationResult:
        """执行硬性校验"""
        pass

# services/validator/soft_validator.py
@dataclass
class SoftValidationResult:
    passed: bool
    quality_score: int           # 0-100
    info_density_score: int      # 信息密度
    title_consistency_score: int # 标题一致性
    is_advertisement: bool       # 是否广告
    timeliness: str              # fresh/recent/outdated
    ai_reasoning: str            # AI 评估理由

class SoftValidator:
    def __init__(self, ai_client: SiliconFlowClient):
        self.ai_client = ai_client
    
    async def validate(self, content: dict) -> SoftValidationResult:
        """执行 AI 软性校验"""
        pass

# services/validator/cross_validator.py
@dataclass
class CrossValidationResult:
    status: str  # multi_source_confirmed/single_source/conflict
    related_contents: list[str]  # 相关内容 ID
    consistency_score: float     # 一致性分数
    conflict_details: str | None # 冲突详情

class CrossValidator:
    async def validate(self, content: dict) -> CrossValidationResult:
        """执行交叉验证"""
        pass
```

### 硅基流动客户端

```python
# services/ai/siliconflow_client.py
class SiliconFlowClient:
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        self.api_key = api_key
        self.base_url = base_url
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> dict:
        """调用 chat/completions 接口"""
        pass
    
    async def evaluate_content_quality(self, content: dict) -> dict:
        """评估内容质量"""
        pass
    
    async def generate_summary(self, content: str, max_length: int = 200) -> dict:
        """生成摘要"""
        pass
    
    async def extract_concepts(self, content: str) -> list[dict]:
        """提取概念"""
        pass
    
    async def classify_content(self, content: dict, nodes: list[dict]) -> dict:
        """内容分类"""
        pass
```

### 抓取调度器

```python
# scheduler/crawl_scheduler.py
class CrawlScheduler:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.job_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """启动调度器"""
        pass
    
    async def stop(self):
        """停止调度器"""
        pass
    
    async def schedule_source(self, source_id: str):
        """调度单个信息源"""
        pass
    
    async def trigger_immediate(self, source_id: str):
        """立即触发抓取"""
        pass
    
    def get_next_crawl_time(self, source: InformationSource) -> datetime:
        """计算下次抓取时间"""
        pass
```


## API 端点（新增）

```python
# 抓取任务相关
GET  /api/crawl-jobs                    # 获取抓取任务列表
GET  /api/crawl-jobs/{job_id}           # 获取任务详情
POST /api/sources/{source_id}/crawl     # 触发即时抓取

# 域名白名单
GET  /api/whitelist                     # 获取白名单列表
POST /api/whitelist                     # 添加域名
DELETE /api/whitelist/{id}              # 移除域名

# 健康监测
GET  /api/sources/{source_id}/health    # 获取信息源健康数据
POST /api/health/check                  # 触发健康检查

# 统计仪表板
GET  /api/dashboard/crawl-stats         # 抓取统计
GET  /api/dashboard/validation-stats    # 校验统计
GET  /api/dashboard/ai-stats            # AI 调用统计
```

## Prompt 模板

### 内容质量评估 Prompt

```python
QUALITY_EVALUATION_PROMPT = """
你是一个内容质量评估专家。请评估以下内容的质量。

标题：{title}
内容：{content}

请从以下维度评估并返回 JSON 格式结果：
1. info_density_score (0-100): 信息密度，内容是否包含有价值的信息
2. title_consistency_score (0-100): 标题与内容的一致性
3. is_advertisement (true/false): 是否为广告或营销内容
4. timeliness: 时效性 (fresh/recent/outdated)
5. reasoning: 评估理由（简短说明）

返回格式：
{{"info_density_score": 80, "title_consistency_score": 90, "is_advertisement": false, "timeliness": "fresh", "reasoning": "..."}}
"""
```

### 摘要生成 Prompt

```python
SUMMARY_GENERATION_PROMPT = """
请为以下内容生成一个简洁的中文摘要，长度在 100-200 字之间。
同时提取 3-5 个关键标签。

内容：{content}

返回格式：
{{"summary": "摘要内容...", "tags": ["标签1", "标签2", "标签3"]}}
"""
```

### 内容分类 Prompt

```python
CONTENT_CLASSIFICATION_PROMPT = """
请将以下内容分类到最相关的知识节点。

内容标题：{title}
内容摘要：{summary}
标签：{tags}

可选节点：
{nodes_list}

请返回最相关的节点（最多 3 个），并给出置信度分数。

返回格式：
{{"classifications": [{{"node_id": "xxx", "confidence": 0.9, "reason": "..."}}]}}
"""
```

## 正确性属性

### Property 1: 信息源状态转换合法性
*For any* 信息源状态变更，新状态必须是当前状态的合法后继状态（按状态机定义）。
**Validates: Requirements 1.1-1.8**

### Property 2: 抓取任务完整性
*For any* 完成的抓取任务，必须记录开始时间、结束时间、状态和抓取数量。
**Validates: Requirements 16.1-16.2**

### Property 3: 去重一致性
*For any* URL 相同的内容，系统中只应存在一条记录（或标记为更新版本）。
**Validates: Requirements 6.1-6.4**

### Property 4: 校验流水线完整性
*For any* 进入系统的内容，必须经过硬性校验；通过硬性校验的内容必须经过软性校验。
**Validates: Requirements 7, 8**

### Property 5: AI 调用重试机制
*For any* AI 服务调用失败，系统应按指数退避策略重试最多 3 次。
**Validates: Requirements 15.4**

### Property 6: 健康度评分范围
*For any* 信息源健康度评分，值必须在 0-100 范围内。
**Validates: Requirements 12.8**

### Property 7: 域名白名单匹配
*For any* 域名查询，通配符匹配应正确处理（如 *.openai.com 匹配 blog.openai.com）。
**Validates: Requirements 14.4**

## 测试策略

### 单元测试
- 各抓取器的解析逻辑
- 校验规则的执行
- 状态机转换逻辑
- 去重算法

### 集成测试
- 完整抓取流程（抓取→去重→校验→存储）
- AI 服务调用
- 调度器任务执行

### Mock 策略
- RSS/API/网页响应使用本地 mock 数据
- AI 服务使用 mock 响应进行单元测试
- 集成测试使用真实 AI 服务（限制调用次数）
