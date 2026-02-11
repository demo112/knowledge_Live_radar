# 设计文档 - 迭代 5：完善与 Docker 化

## 概述

本设计文档描述 AI Radar 系统迭代 5 的技术实现方案。迭代 5 是最终迭代，聚焦于：
- 全文搜索与高级过滤
- AI 提示词管理与 A/B 测试
- 数据导入导出
- 通知系统完善
- 性能优化（缓存、异步、索引）
- 系统监控仪表板
- API 速率限制
- Docker 容器化部署
- 错误处理完善

本迭代聚焦于主需求文档中的需求 30（日志与监控）、需求 32（Docker 部署）、需求 40（搜索与过滤）、需求 41（通知系统）、需求 42（数据导入导出）、需求 45（AI 提示词管理）、需求 47（性能优化）、需求 48（错误处理与恢复）的完整实现。

## 架构设计

### 整体架构（Docker 部署视图）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose                                    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Nginx (可选反向代理)                          │  │
│  └──────────────────────────┬───────────────────────────────────────────┘  │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                          │
│         ▼                                       ▼                          │
│  ┌──────────────┐                        ┌──────────────┐                  │
│  │   Frontend   │                        │   Backend    │                  │
│  │  (Next.js)   │───────────────────────▶│  (FastAPI)   │                  │
│  │  Port: 3000  │                        │  Port: 8000  │                  │
│  └──────────────┘                        └──────┬───────┘                  │
│                                                  │                          │
│                              ┌───────────────────┼───────────────┐         │
│                              ▼                                   ▼         │
│                       ┌──────────────┐                    ┌──────────────┐ │
│                       │  PostgreSQL  │                    │    Redis     │ │
│                       │  Port: 5432  │                    │  Port: 6379  │ │
│                       └──────────────┘                    └──────────────┘ │
│                              │                                   │         │
│                       ┌──────┴──────┐                    ┌──────┴──────┐  │
│                       │  db_data    │                    │ redis_data  │  │
│                       │  (volume)   │                    │  (volume)   │  │
│                       └─────────────┘                    └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 新增功能模块架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              请求处理层                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ Rate_Limiter │  │ Auth_Middle  │  │ Error_Handler│                      │
│  │  (中间件)    │  │  ware        │  │  (中间件)    │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                              缓存层                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Cache_Service (Redis)                          │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │  │
│  │  │ 金字塔缓存     │  │ 搜索结果缓存   │  │ 指标缓存       │         │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                              新增服务层                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │ Search_Service │  │ Prompt_Manager │  │ Export/Import  │                │
│  │  (全文搜索)    │  │  (提示词管理)  │  │  _Service      │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │ Notification   │  │ Performance    │  │ Metrics        │                │
│  │  _Service      │  │  _Monitor      │  │  _Collector    │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 目录结构（新增）

```
backend/
├── app/
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── rate_limiter.py               # 速率限制中间件
│   │   ├── error_handler.py              # 全局错误处理中间件
│   │   └── performance_tracker.py        # 性能追踪中间件
│   ├── services/
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   └── search_service.py         # 全文搜索服务
│   │   ├── prompt/
│   │   │   ├── __init__.py
│   │   │   └── prompt_manager.py         # 提示词管理服务
│   │   ├── notification/
│   │   │   ├── __init__.py
│   │   │   ├── notification_service.py   # 通知服务
│   │   │   └── channels/
│   │   │       ├── __init__.py
│   │   │       ├── in_app.py             # 站内通知
│   │   │       └── webhook.py            # Webhook 通知
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── export_service.py         # 数据导出服务
│   │   │   └── import_service.py         # 数据导入服务
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── cache_service.py          # 缓存服务
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       ├── metrics_collector.py      # 指标收集器
│   │       └── performance_monitor.py    # 性能监控器
│   ├── api/
│   │   ├── search.py                     # 搜索 API
│   │   ├── prompts.py                    # 提示词管理 API
│   │   ├── notifications.py             # 通知 API
│   │   ├── data_transfer.py             # 导入导出 API
│   │   └── monitoring.py                # 监控 API
│   └── models/
│       ├── prompt_template.py            # 提示词模板模型
│       ├── prompt_version.py             # 提示词版本模型
│       ├── ab_test.py                    # A/B 测试模型
│       ├── notification.py               # 通知模型
│       ├── notification_preference.py    # 通知偏好模型
│       ├── api_metric.py                # API 指标模型
│       └── error_record.py              # 错误记录模型
├── Dockerfile                            # 后端 Dockerfile
├── .dockerignore

frontend/
├── src/
│   ├── app/
│   │   ├── search/
│   │   │   └── page.tsx                  # 搜索页面
│   │   ├── prompts/
│   │   │   └── page.tsx                  # 提示词管理页面
│   │   ├── monitor/
│   │   │   └── page.tsx                  # 监控仪表板页面
│   │   └── data/
│   │       └── page.tsx                  # 数据管理页面
│   └── components/
│       ├── search/
│       │   ├── SearchBar.tsx             # 搜索栏
│       │   ├── SearchFilters.tsx         # 高级过滤面板
│       │   └── SearchResults.tsx         # 搜索结果列表
│       ├── prompts/
│       │   ├── PromptEditor.tsx          # 提示词编辑器
│       │   ├── PromptTester.tsx          # 提示词测试面板
│       │   └── ABTestPanel.tsx           # A/B 测试面板
│       ├── monitor/
│       │   ├── SystemOverview.tsx        # 系统概览
│       │   ├── PerformanceCharts.tsx     # 性能图表
│       │   ├── AIMetrics.tsx             # AI 指标
│       │   ├── BusinessMetrics.tsx       # 业务指标
│       │   └── ErrorLog.tsx              # 错误日志
│       ├── data/
│       │   ├── ExportPanel.tsx           # 导出面板
│       │   └── ImportPanel.tsx           # 导入面板
│       └── common/
│           └── NotificationBell.tsx      # 通知铃铛组件
├── Dockerfile                            # 前端 Dockerfile
├── .dockerignore

# Docker 配置（项目根目录）
docker-compose.yml                        # 生产环境编排
docker-compose.dev.yml                    # 开发环境编排
.env.example                              # 环境变量模板
```

## 数据模型

### 提示词模板 (Prompt_Template)

```python
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id: str                      # UUID
    scene: str                   # quality_eval/summary/concept_extract/classify/proposal/structure_analysis/drift_detection/strategy_optimization
    name: str                    # 模板名称
    description: str             # 模板说明
    current_version_id: str | None  # 当前使用的版本 ID
    
    created_at: datetime
    updated_at: datetime
```

### 提示词版本 (Prompt_Version)

```python
class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    
    id: str                      # UUID
    template_id: str             # 模板 ID
    version: int                 # 版本号
    content: str                 # 提示词内容
    variables: list[str]         # 变量列表
    
    # 效果指标
    call_count: int              # 调用次数
    avg_latency_ms: float        # 平均耗时
    avg_quality_score: float     # 平均质量评分
    error_rate: float            # 错误率
    
    created_at: datetime
    created_by: str              # 创建者
```

### A/B 测试 (AB_Test)

```python
class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id: str                      # UUID
    template_id: str             # 模板 ID
    version_a_id: str            # 版本 A ID
    version_b_id: str            # 版本 B ID
    traffic_ratio: float         # 版本 A 的流量比例 (0-1)
    
    status: str                  # running/completed/cancelled
    started_at: datetime
    ended_at: datetime | None
    
    # 结果
    version_a_calls: int
    version_b_calls: int
    version_a_avg_quality: float
    version_b_avg_quality: float
    winner_version_id: str | None
```

### 通知 (Notification)

```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id: str                      # UUID
    level: str                   # info/warning/critical
    title: str                   # 通知标题
    message: str                 # 通知内容
    source_type: str             # proposal/source_health/system_health/ai_service/task
    source_id: str | None        # 关联对象 ID
    
    is_read: bool                # 是否已读
    read_at: datetime | None
    
    # 发送渠道
    channels_sent: list[str]     # ["in_app", "webhook"]
    webhook_status: str | None   # success/failed/skipped
    
    created_at: datetime
```

### 通知偏好 (Notification_Preference)

```python
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id: str                      # UUID
    
    # 渠道配置
    in_app_enabled: bool         # 站内通知开关
    webhook_enabled: bool        # Webhook 开关
    webhook_url: str | None      # Webhook URL
    
    # 级别过滤
    min_level: str               # 最低通知级别 info/warning/critical
    
    # 静默时段
    quiet_hours_enabled: bool
    quiet_hours_start: str       # "22:00"
    quiet_hours_end: str         # "08:00"
    quiet_hours_allow_critical: bool  # 静默时段是否允许紧急通知
    
    updated_at: datetime
```

### API 指标 (API_Metric)

```python
class APIMetric(Base):
    __tablename__ = "api_metrics"
    
    id: str                      # UUID
    endpoint: str                # API 端点路径
    method: str                  # HTTP 方法
    status_code: int             # 响应状态码
    response_time_ms: float      # 响应时间（毫秒）
    
    created_at: datetime
```

### 错误记录 (Error_Record)

```python
class ErrorRecord(Base):
    __tablename__ = "error_records"
    
    id: str                      # UUID
    error_type: str              # network/ai_service/database/validation/unknown
    error_message: str           # 错误信息
    stack_trace: str | None      # 堆栈信息
    context: dict                # 上下文信息
    
    source_service: str          # 来源服务
    source_task_id: str | None   # 关联任务 ID
    
    retry_count: int             # 已重试次数
    max_retries: int             # 最大重试次数
    is_resolved: bool            # 是否已解决
    resolved_at: datetime | None
    
    created_at: datetime
```

## 组件接口设计

### 全文搜索服务

```python
# services/search/search_service.py
from dataclasses import dataclass

@dataclass
class SearchQuery:
    keyword: str                 # 搜索关键词
    boolean_mode: bool           # 是否启用布尔模式
    node_ids: list[str] | None   # 金字塔节点过滤
    include_children: bool       # 是否包含子节点
    time_start: datetime | None  # 时间范围开始
    time_end: datetime | None    # 时间范围结束
    min_quality_score: int | None  # 最低质量分数
    validation_status: list[str] | None  # 验证状态过滤
    sort_by: str                 # relevance/time/quality
    sort_order: str              # asc/desc

@dataclass
class SearchResult:
    total: int                   # 总结果数
    items: list[dict]            # 结果列表（含高亮片段）
    facets: dict                 # 聚合统计（按节点、状态等）

class SearchService:
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    async def search(self, query: SearchQuery, page: int = 1, size: int = 20) -> SearchResult:
        """执行全文搜索"""
        pass
    
    async def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """搜索建议（基于历史搜索和热门标签）"""
        pass
    
    def highlight(self, text: str, keywords: list[str]) -> str:
        """高亮关键词"""
        pass
    
    def parse_boolean_query(self, query: str) -> dict:
        """解析布尔查询（AND/OR/NOT）"""
        pass
```

### 提示词管理服务

```python
# services/prompt/prompt_manager.py
@dataclass
class PromptTestResult:
    version_id: str
    input_data: dict
    output: str
    latency_ms: float
    token_usage: dict

class PromptManager:
    def __init__(self, ai_client: SiliconFlowClient):
        self.ai_client = ai_client
    
    async def list_templates(self) -> list[PromptTemplate]:
        """列出所有提示词模板"""
        pass
    
    async def get_template(self, template_id: str) -> PromptTemplate:
        """获取模板详情"""
        pass
    
    async def create_version(self, template_id: str, content: str, created_by: str) -> PromptVersion:
        """创建新版本"""
        pass
    
    async def set_active_version(self, template_id: str, version_id: str) -> None:
        """设置当前使用版本"""
        pass
    
    async def test_prompt(self, version_id: str, test_input: dict) -> PromptTestResult:
        """测试提示词"""
        pass
    
    async def get_version_history(self, template_id: str) -> list[PromptVersion]:
        """获取版本历史"""
        pass
    
    async def start_ab_test(self, template_id: str, version_a_id: str, version_b_id: str, traffic_ratio: float) -> ABTest:
        """启动 A/B 测试"""
        pass
    
    async def stop_ab_test(self, test_id: str) -> ABTest:
        """停止 A/B 测试"""
        pass
    
    async def get_prompt_for_scene(self, scene: str, variables: dict) -> str:
        """获取指定场景的提示词（支持 A/B 测试分流）"""
        pass
    
    async def record_prompt_metrics(self, version_id: str, latency_ms: float, quality_score: float, is_error: bool) -> None:
        """记录提示词效果指标"""
        pass
```

### 通知服务

```python
# services/notification/notification_service.py
from enum import Enum

class NotificationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class NotificationService:
    def __init__(self, preference: NotificationPreference):
        self.preference = preference
        self.channels = []
    
    async def send(self, level: NotificationLevel, title: str, message: str, source_type: str, source_id: str | None = None) -> Notification:
        """发送通知"""
        pass
    
    async def is_quiet_hours(self) -> bool:
        """检查是否在静默时段"""
        pass
    
    async def list_notifications(self, is_read: bool | None = None, page: int = 1, size: int = 20) -> list[Notification]:
        """获取通知列表"""
        pass
    
    async def mark_read(self, notification_id: str) -> None:
        """标记已读"""
        pass
    
    async def mark_all_read(self) -> None:
        """全部标记已读"""
        pass
    
    async def get_unread_count(self) -> int:
        """获取未读数量"""
        pass
    
    async def update_preference(self, preference: NotificationPreference) -> None:
        """更新通知偏好"""
        pass
```

### 数据导入导出服务

```python
# services/data/export_service.py
@dataclass
class ExportOptions:
    include_content: bool        # 是否包含内容
    include_sources: bool        # 是否包含信息源配置
    pyramid_ids: list[str] | None  # 指定金字塔（None 表示全部）

@dataclass
class ExportResult:
    file_path: str
    file_size: int
    pyramid_count: int
    node_count: int
    content_count: int
    source_count: int

class ExportService:
    async def export_data(self, options: ExportOptions) -> ExportResult:
        """导出数据为 JSON"""
        pass
    
    async def export_pyramid(self, pyramid_id: str, include_content: bool = False) -> dict:
        """导出单个金字塔"""
        pass
    
    async def export_sources(self) -> list[dict]:
        """导出信息源配置（脱敏）"""
        pass

# services/data/import_service.py
@dataclass
class ImportConflict:
    type: str                    # pyramid/node/source
    existing_name: str
    import_name: str
    resolution: str | None       # skip/overwrite/rename

@dataclass
class ImportResult:
    success: bool
    pyramid_count: int
    node_count: int
    content_count: int
    source_count: int
    conflicts: list[ImportConflict]
    errors: list[str]

class ImportService:
    async def validate_import_data(self, data: dict) -> tuple[bool, list[str]]:
        """验证导入数据格式"""
        pass
    
    async def detect_conflicts(self, data: dict) -> list[ImportConflict]:
        """检测导入冲突"""
        pass
    
    async def import_data(self, data: dict, conflict_resolutions: dict[str, str] | None = None) -> ImportResult:
        """执行导入"""
        pass
```

### 缓存服务

```python
# services/cache/cache_service.py
class CacheService:
    # 缓存 TTL 配置
    PYRAMID_CACHE_TTL = 300      # 5 分钟
    SEARCH_CACHE_TTL = 60        # 1 分钟
    METRICS_CACHE_TTL = 30       # 30 秒
    
    def __init__(self, redis_url: str | None = None):
        """初始化缓存（支持 Redis 和内存回退）"""
        pass
    
    async def get(self, key: str) -> str | None:
        """获取缓存"""
        pass
    
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """设置缓存"""
        pass
    
    async def delete(self, key: str) -> None:
        """删除缓存"""
        pass
    
    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        pass
    
    async def invalidate_pyramid(self, pyramid_id: str) -> None:
        """失效金字塔相关缓存"""
        pass
    
    async def invalidate_search(self) -> None:
        """失效搜索缓存"""
        pass
```

### 性能监控器

```python
# services/monitoring/performance_monitor.py
@dataclass
class PerformanceSnapshot:
    timestamp: datetime
    api_metrics: dict            # {endpoint: {avg_ms, p95_ms, count, error_rate}}
    db_metrics: dict             # {avg_query_ms, connection_pool_usage}
    ai_metrics: dict             # {call_count, avg_latency_ms, success_rate, total_tokens}
    system_metrics: dict         # {memory_mb, cpu_percent, disk_usage_percent}

class PerformanceMonitor:
    SLOW_QUERY_THRESHOLD_MS = 3000
    
    async def record_api_call(self, endpoint: str, method: str, status_code: int, response_time_ms: float) -> None:
        """记录 API 调用指标"""
        pass
    
    async def record_ai_call(self, scene: str, latency_ms: float, tokens: int, success: bool) -> None:
        """记录 AI 调用指标"""
        pass
    
    async def get_snapshot(self, time_range: str = "1h") -> PerformanceSnapshot:
        """获取性能快照"""
        pass
    
    async def get_api_metrics(self, time_range: str = "1h") -> dict:
        """获取 API 指标"""
        pass
    
    async def get_slow_queries(self, limit: int = 20) -> list[dict]:
        """获取慢查询日志"""
        pass
    
    async def get_error_stats(self, time_range: str = "1h") -> dict:
        """获取错误统计"""
        pass
```

### 速率限制中间件

```python
# middleware/rate_limiter.py
class RateLimiter:
    # 默认限制配置
    DEFAULT_LIMITS = {
        "default": {"requests": 60, "window_seconds": 60},
        "ai": {"requests": 10, "window_seconds": 60},
        "export": {"requests": 5, "window_seconds": 300},
    }
    
    def __init__(self, cache_service: CacheService, config_service: ConfigurationService):
        self.cache_service = cache_service
        self.config_service = config_service
    
    async def check_rate_limit(self, client_ip: str, endpoint_category: str) -> tuple[bool, int]:
        """检查速率限制，返回 (是否允许, 剩余等待秒数)"""
        pass
    
    async def record_request(self, client_ip: str, endpoint_category: str) -> None:
        """记录请求"""
        pass
```

### 全局错误处理中间件

```python
# middleware/error_handler.py
from dataclasses import dataclass

@dataclass
class RetryPolicy:
    max_retries: int
    base_delay_seconds: float
    backoff_factor: float        # 指数退避因子

class ErrorHandler:
    # 重试策略配置
    RETRY_POLICIES = {
        "network": RetryPolicy(max_retries=3, base_delay_seconds=1, backoff_factor=1.5),
        "ai_service": RetryPolicy(max_retries=3, base_delay_seconds=5, backoff_factor=2.0),
        "database": RetryPolicy(max_retries=0, base_delay_seconds=0, backoff_factor=0),  # 不重试
    }
    
    # 熔断配置
    CIRCUIT_BREAKER_THRESHOLD = 10   # 5 分钟内错误次数
    CIRCUIT_BREAKER_WINDOW = 300     # 5 分钟窗口
    
    async def handle_error(self, error: Exception, context: dict) -> None:
        """处理错误（记录、重试、告警）"""
        pass
    
    async def should_circuit_break(self, error_type: str) -> bool:
        """检查是否应触发熔断"""
        pass
    
    async def record_error(self, error_type: str, message: str, context: dict) -> ErrorRecord:
        """记录错误"""
        pass
    
    async def get_failed_tasks(self, page: int = 1, size: int = 20) -> list[ErrorRecord]:
        """获取失败任务列表"""
        pass
    
    async def retry_failed_task(self, error_id: str) -> bool:
        """手动重试失败任务"""
        pass
```

## API 端点

```python
# 搜索
GET  /api/search                           # 全文搜索
GET  /api/search/suggest                   # 搜索建议

# 提示词管理
GET  /api/prompts                          # 获取所有模板
GET  /api/prompts/{id}                     # 获取模板详情
POST /api/prompts/{id}/versions            # 创建新版本
PUT  /api/prompts/{id}/active-version      # 设置当前版本
POST /api/prompts/versions/{id}/test       # 测试提示词
GET  /api/prompts/{id}/versions            # 获取版本历史
POST /api/prompts/{id}/ab-test             # 启动 A/B 测试
PUT  /api/prompts/ab-tests/{id}/stop       # 停止 A/B 测试
GET  /api/prompts/ab-tests/{id}            # 获取 A/B 测试结果

# 通知
GET  /api/notifications                    # 获取通知列表
GET  /api/notifications/unread-count       # 获取未读数量
PUT  /api/notifications/{id}/read          # 标记已读
PUT  /api/notifications/read-all           # 全部标记已读
GET  /api/notifications/preferences        # 获取通知偏好
PUT  /api/notifications/preferences        # 更新通知偏好

# 数据导入导出
POST /api/data/export                      # 导出数据
POST /api/data/import/validate             # 验证导入数据
POST /api/data/import                      # 执行导入
GET  /api/data/export/{task_id}            # 获取导出任务状态/下载

# 监控
GET  /api/monitoring/snapshot              # 获取性能快照
GET  /api/monitoring/api-metrics           # 获取 API 指标
GET  /api/monitoring/ai-metrics            # 获取 AI 指标
GET  /api/monitoring/business-metrics      # 获取业务指标
GET  /api/monitoring/errors                # 获取错误统计
GET  /api/monitoring/errors/list           # 获取错误列表
POST /api/monitoring/errors/{id}/retry     # 手动重试失败任务
GET  /api/monitoring/slow-queries          # 获取慢查询日志
```

## Docker 配置

### docker-compose.yml

```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
      - SILICONFLOW_BASE_URL=${SILICONFLOW_BASE_URL:-https://api.siliconflow.cn/v1}
      - AI_MODEL_NAME=${AI_MODEL_NAME:-deepseek-chat}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - upload_data:/app/uploads
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=${DB_USER:-airadar}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-airadar_pass}
      - POSTGRES_DB=${DB_NAME:-airadar}
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-airadar}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db_data:
  redis_data:
  upload_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 运行数据库迁移并启动服务
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Frontend Dockerfile

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build

# 运行阶段
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### .env.example

```bash
# 数据库
DB_USER=airadar
DB_PASSWORD=airadar_pass
DB_NAME=airadar
DB_PORT=5432

# Redis
REDIS_PORT=6379

# 后端
BACKEND_PORT=8000
LOG_LEVEL=INFO

# 前端
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# AI 服务
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
AI_MODEL_NAME=deepseek-chat

# 通知
WEBHOOK_URL=
```

## 数据库索引优化

```sql
-- 内容搜索优化
CREATE INDEX idx_content_items_title_trgm ON content_items USING gin (title gin_trgm_ops);
CREATE INDEX idx_content_items_summary_trgm ON content_items USING gin (summary gin_trgm_ops);
CREATE INDEX idx_content_items_node_created ON content_items (node_id, created_at DESC);
CREATE INDEX idx_content_items_quality_score ON content_items (quality_score DESC);
CREATE INDEX idx_content_items_validation_status ON content_items (validation_status);

-- 信息源查询优化
CREATE INDEX idx_sources_status_health ON information_sources (lifecycle_status, health_score DESC);

-- API 指标查询优化
CREATE INDEX idx_api_metrics_endpoint_time ON api_metrics (endpoint, created_at DESC);
CREATE INDEX idx_api_metrics_created_at ON api_metrics (created_at DESC);

-- 错误记录查询优化
CREATE INDEX idx_error_records_type_time ON error_records (error_type, created_at DESC);
CREATE INDEX idx_error_records_unresolved ON error_records (is_resolved, created_at DESC) WHERE is_resolved = false;

-- 通知查询优化
CREATE INDEX idx_notifications_unread ON notifications (is_read, created_at DESC) WHERE is_read = false;

-- 提示词版本查询优化
CREATE INDEX idx_prompt_versions_template ON prompt_versions (template_id, version DESC);
```

## 正确性属性

### Property 1: 搜索结果相关性
*For any* 全文搜索查询，返回的每个结果必须在标题、摘要或标签中包含至少一个搜索关键词（布尔 NOT 排除的除外）。
**Validates: Requirements 1.1**

### Property 2: 布尔搜索语义正确性
*For any* 布尔搜索查询 "A AND B"，返回的每个结果必须同时包含 A 和 B；对于 "A OR B"，每个结果必须包含 A 或 B；对于 "A NOT B"，每个结果必须包含 A 且不包含 B。
**Validates: Requirements 1.2**

### Property 3: 节点过滤层级完整性
*For any* 按金字塔节点过滤的搜索，返回结果必须包含该节点及其所有后代节点下的内容，不遗漏也不多余。
**Validates: Requirements 1.3**

### Property 4: 提示词版本链完整性
*For any* 提示词模板，其版本列表必须按版本号升序排列，版本号连续递增，且当前使用版本必须存在于版本列表中。
**Validates: Requirements 2.2**

### Property 5: A/B 测试流量分配正确性
*For any* 运行中的 A/B 测试，在足够多的请求（>100）后，版本 A 的实际流量比例与配置比例的偏差不超过 10%。
**Validates: Requirements 2.4**

### Property 6: 导出导入往返一致性
*For any* 金字塔导出后再导入，导入后的金字塔结构（节点层级、名称、描述）必须与导出前完全一致。
**Validates: Requirements 3.1, 3.4**

### Property 7: 导入冲突检测完整性
*For any* 导入操作，如果导入数据中的金字塔名称与现有金字塔名称重复，必须报告冲突。
**Validates: Requirements 3.6**

### Property 8: 通知静默时段遵守
*For any* 非紧急通知，如果当前时间在配置的静默时段内，则不应通过非站内渠道发送。紧急通知不受静默时段限制（如果配置允许）。
**Validates: Requirements 4.8**

### Property 9: 通知级别过滤正确性
*For any* 通知发送请求，如果通知级别低于配置的最低级别，则不应发送。
**Validates: Requirements 4.7**

### Property 10: 缓存失效及时性
*For any* 金字塔结构变更操作（添加/删除/移动节点），变更后立即查询金字塔可视化数据应返回更新后的结果，不应返回过期缓存。
**Validates: Requirements 5.3**

### Property 11: 速率限制正确性
*For any* 客户端 IP，在配置的时间窗口内，成功请求数不应超过配置的最大请求数。超过限制的请求必须返回 429 状态码。
**Validates: Requirements 7.1, 7.3**

### Property 12: 错误重试策略遵守
*For any* 失败的任务，重试次数不应超过对应错误类型的最大重试次数，且重试间隔应遵循指数退避策略。
**Validates: Requirements 9.1, 9.3**

### Property 13: 熔断机制触发正确性
*For any* 错误类型，如果在 5 分钟窗口内同类错误超过 10 次，后续同类操作应被熔断（快速失败），直到窗口过期。
**Validates: Requirements 9.4**

### Property 14: 导出数据脱敏
*For any* 信息源配置导出，敏感字段（API 密钥、认证令牌）必须被脱敏处理，不应包含明文敏感信息。
**Validates: Requirements 3.3**

### Property 15: API 指标记录完整性
*For any* API 请求，必须记录端点路径、HTTP 方法、状态码和响应时间，且响应时间为非负数。
**Validates: Requirements 5.6**

## 错误处理

### 新增错误码

```python
ERROR_CODES = {
    # 搜索错误
    "SEARCH_QUERY_INVALID": "搜索查询语法无效",
    "SEARCH_TIMEOUT": "搜索超时",
    
    # 提示词错误
    "PROMPT_TEMPLATE_NOT_FOUND": "提示词模板不存在",
    "PROMPT_VERSION_NOT_FOUND": "提示词版本不存在",
    "PROMPT_TEST_FAILED": "提示词测试执行失败",
    "AB_TEST_ALREADY_RUNNING": "该模板已有运行中的 A/B 测试",
    "AB_TEST_NOT_FOUND": "A/B 测试不存在",
    
    # 导入导出错误
    "EXPORT_FAILED": "数据导出失败",
    "IMPORT_VALIDATION_FAILED": "导入数据格式验证失败",
    "IMPORT_CONFLICT": "导入数据存在冲突",
    "IMPORT_FAILED": "数据导入失败",
    
    # 通知错误
    "NOTIFICATION_NOT_FOUND": "通知不存在",
    "WEBHOOK_DELIVERY_FAILED": "Webhook 发送失败",
    
    # 速率限制
    "RATE_LIMIT_EXCEEDED": "请求频率超过限制",
    
    # 监控错误
    "METRICS_QUERY_FAILED": "指标查询失败",
    
    # 熔断
    "CIRCUIT_BREAKER_OPEN": "服务熔断中，请稍后重试",
}
```

### 错误处理策略

| 错误类型 | 处理方式 | HTTP 状态码 |
|---------|---------|------------|
| 搜索语法错误 | 返回错误说明和正确语法示例 | 400 |
| 搜索超时 | 返回部分结果和超时提示 | 200 (partial) |
| 导入验证失败 | 返回详细验证错误列表 | 422 |
| 导入冲突 | 返回冲突列表，等待用户选择解决方案 | 409 |
| 速率限制 | 返回 Retry-After 头 | 429 |
| 服务熔断 | 返回熔断状态和预计恢复时间 | 503 |
| Webhook 发送失败 | 记录失败，不影响站内通知 | - |

## 测试策略

### 单元测试

- 搜索查询解析（布尔运算符、关键词提取）
- 缓存失效逻辑（变更触发、TTL 过期）
- 速率限制计数逻辑（窗口滑动、计数器）
- 通知过滤逻辑（级别过滤、静默时段）
- 导入数据验证逻辑（格式检查、冲突检测）
- 错误重试策略（指数退避计算、熔断判断）
- 提示词 A/B 测试分流逻辑

### 属性测试

使用 Hypothesis 库进行属性测试，每个属性测试运行至少 100 次迭代。

测试标签格式：`Feature: ai-radar-iteration-5, Property N: {property_text}`

```python
from hypothesis import given, strategies as st

# 搜索查询策略
keyword_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))
boolean_query_strategy = st.one_of(
    keyword_strategy,
    st.tuples(keyword_strategy, st.sampled_from(['AND', 'OR', 'NOT']), keyword_strategy).map(lambda t: f"{t[0]} {t[1]} {t[2]}")
)

# 速率限制策略
request_count_strategy = st.integers(min_value=1, max_value=200)
window_seconds_strategy = st.integers(min_value=1, max_value=300)

# 通知级别策略
notification_level_strategy = st.sampled_from(['info', 'warning', 'critical'])

# 导出导入策略
pyramid_data_strategy = st.fixed_dictionaries({
    'name': st.text(min_size=1, max_size=100),
    'description': st.text(max_size=500),
    'nodes': st.lists(st.fixed_dictionaries({
        'name': st.text(min_size=1, max_size=100),
        'description': st.text(max_size=500),
    }), max_size=20)
})
```

### 集成测试

- 全文搜索端到端流程（创建内容→搜索→验证结果）
- 提示词 A/B 测试完整流程（创建版本→启动测试→记录指标→停止测试→查看结果）
- 数据导出导入往返测试（导出→导入→对比）
- 通知发送完整流程（触发事件→过滤→发送→记录）
- 缓存失效测试（修改数据→验证缓存更新）
- 速率限制测试（超过限制→验证 429 响应）
- Docker 部署测试（docker-compose up→健康检查→基本功能验证）

### Mock 策略

- AI 服务使用 mock 响应进行单元测试
- Redis 使用 fakeredis 进行缓存测试
- Webhook 使用 mock server 进行通知测试
- 集成测试使用 docker-compose.test.yml 启动完整环境
