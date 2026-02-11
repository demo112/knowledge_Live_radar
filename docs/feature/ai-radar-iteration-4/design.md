# 设计文档 - 迭代 4：自我进化

## 概述

本设计文档描述 AI Radar 系统迭代 4 的技术实现方案。迭代 4 的目标是实现系统的自我进化能力，包括：
- 系统全面健康检测机制
- 金字塔结构重构建议引擎
- 热点话题生命周期自动管理
- 概念漂移检测与术语更新
- 抓取策略自适应优化
- 健康报告可视化界面
- 定时任务统一调度管理
- 系统配置热更新管理

本迭代聚焦于主需求文档中的需求 17（系统健康检测）、需求 18（金字塔重构建议）、需求 19（热点生命周期管理）、需求 20（概念漂移检测）、需求 21（抓取策略自适应）、需求 26（健康报告界面）、需求 29（系统配置管理）、需求 46（定时任务管理）的实现。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              定时调度层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Scheduler_Service                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │ 内容抓取   │  │ 健康检查   │  │ 热点更新   │  │ 漂移检测   │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              健康检测层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Health_Detector                                │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │  │
│  │  │ 金字塔结构评估 │  │ 信息源健康评估 │  │ 内容覆盖评估   │         │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │  │
│  │  ┌────────────────┐  ┌────────────────┐                             │  │
│  │  │ 热点分布评估   │  │ 审批积压评估   │                             │  │
│  │  └────────────────┘  └────────────────┘                             │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              自我进化层                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │Restructure     │  │Hotspot         │  │Concept_Drift   │                │
│  │  _Advisor      │  │  _Manager      │  │  _Detector     │                │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                │
│          │                   │                    │                          │
│  ┌───────┴───────────────────┴────────────────────┴────────┐               │
│  │                    Strategy_Optimizer                     │               │
│  └──────────────────────────┬───────────────────────────────┘               │
└─────────────────────────────┼──────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              提案生成层（复用迭代 3）                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │Proposal        │  │Approval_Queue  │  │Decision        │                │
│  │  _Generator    │  │  _Manager      │  │  _Executor     │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              配置管理层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Configuration_Service                             │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │  │
│  │  │ 环境变量加载   │  │ 配置文件解析   │  │ 热更新监听     │         │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 热点生命周期状态机

```
                    ┌──────────────┐
                    │   emerging   │ ← 新兴（频率超过阈值）
                    └──────┬───────┘
                           │ 频率持续增长
                           ▼
                    ┌──────────────┐
                    │   trending   │ ← 热门
                    └──────┬───────┘
                           │ 增长放缓
                           ▼
                    ┌──────────────┐
                    │    mature    │ ← 成熟
                    └──────┬───────┘
                           │ 频率连续下降
                           ▼
                    ┌──────────────┐
                    │   cooling    │ ← 冷却
                    └──────┬───────┘
                           │ 长期无更新
                           ▼
                    ┌──────────────┐
                    │   archived   │ ← 归档
                    └──────────────┘

注：管理员可手动调整任意状态
```

## 目录结构（新增）

```
backend/
├── app/
│   ├── services/
│   │   ├── evolution/                    # 自我进化模块
│   │   │   ├── __init__.py
│   │   │   ├── health_detector.py        # 系统健康检测器
│   │   │   ├── restructure_advisor.py    # 金字塔重构建议器
│   │   │   ├── hotspot_manager.py        # 热点生命周期管理器
│   │   │   ├── concept_drift_detector.py # 概念漂移检测器
│   │   │   └── strategy_optimizer.py     # 抓取策略优化器
│   │   ├── scheduler/                    # 定时任务调度
│   │   │   ├── __init__.py
│   │   │   ├── scheduler_service.py      # 调度服务
│   │   │   └── task_registry.py          # 任务注册表
│   │   └── config/                       # 配置管理
│   │       ├── __init__.py
│   │       └── configuration_service.py  # 配置服务
│   ├── api/
│   │   ├── health_report.py              # 健康报告 API
│   │   ├── scheduler.py                  # 定时任务 API
│   │   └── config.py                     # 配置管理 API
│   └── models/
│       ├── hotspot.py                    # 热点话题模型
│       ├── hotspot_event.py              # 热点事件记录模型
│       ├── concept_definition.py         # 概念定义版本模型
│       ├── health_report.py              # 健康报告模型
│       ├── strategy_adjustment.py        # 策略调整记录模型
│       ├── scheduled_task.py             # 定时任务模型
│       ├── task_execution.py             # 任务执行记录模型
│       └── config_history.py             # 配置变更历史模型

frontend/
├── src/
│   ├── app/
│   │   ├── health/                       # 健康报告
│   │   │   └── page.tsx
│   │   ├── tasks/                        # 任务管理
│   │   │   └── page.tsx
│   │   └── settings/                     # 系统配置
│   │       └── page.tsx
│   └── components/
│       ├── health/                       # 健康报告组件
│       │   ├── HealthOverview.tsx
│       │   ├── PyramidHealthCard.tsx
│       │   ├── SourceHealthSummary.tsx
│       │   ├── HotspotDistribution.tsx
│       │   ├── CrawlStats.tsx
│       │   └── ApprovalBacklog.tsx
│       ├── tasks/                        # 任务管理组件
│       │   ├── TaskList.tsx
│       │   ├── TaskDetail.tsx
│       │   └── ExecutionHistory.tsx
│       └── settings/                     # 配置组件
│           ├── ConfigForm.tsx
│           ├── ConfigHistory.tsx
│           └── ConfigGroup.tsx
```


## 数据模型

### 热点话题 (Hotspot)

```python
class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id: str                      # UUID
    topic_name: str              # 话题名称
    description: str             # 话题描述
    status: str                  # emerging/trending/mature/cooling/archived
    
    # 频率统计
    mention_count: int           # 总提及次数
    recent_7d_count: int         # 近 7 天提及次数
    previous_7d_count: int       # 前 7 天提及次数
    growth_rate: float           # 增长率
    
    # 优先级
    display_priority: float      # 展示优先级权重 0-1
    
    # 关联
    related_node_ids: list[str]  # 关联的金字塔节点 ID
    related_content_ids: list[str]  # 关联的内容 ID
    
    # 时间
    first_seen_at: datetime      # 首次出现时间
    last_mentioned_at: datetime  # 最后提及时间
    status_changed_at: datetime  # 最后状态变更时间
    created_at: datetime
    updated_at: datetime
```

### 热点事件记录 (Hotspot_Event)

```python
class HotspotEvent(Base):
    __tablename__ = "hotspot_events"
    
    id: str                      # UUID
    hotspot_id: str              # 热点 ID
    event_type: str              # state_change/manual_adjust/mention
    
    old_status: str | None       # 旧状态
    new_status: str | None       # 新状态
    trigger_condition: str       # 触发条件描述
    operator: str | None         # 操作者（手动调整时）
    
    created_at: datetime
```

### 概念定义版本 (Concept_Definition)

```python
class ConceptDefinition(Base):
    __tablename__ = "concept_definitions"
    
    id: str                      # UUID
    term: str                    # 术语名称
    definition: str              # 定义内容
    context_examples: list[str]  # 上下文示例
    version: int                 # 版本号
    
    # 漂移信息
    drift_detected: bool         # 是否检测到漂移
    drift_evidence: str | None   # 漂移证据
    previous_version_id: str | None  # 前一版本 ID
    proposal_id: str | None      # 关联的变更提案 ID
    
    created_at: datetime
    is_current: bool             # 是否为当前版本
```

### 健康报告 (Health_Report)

```python
class HealthReport(Base):
    __tablename__ = "health_reports"
    
    id: str                      # UUID
    report_type: str             # daily/manual
    
    # 各维度评分
    overall_score: int           # 系统整体评分 0-100
    pyramid_scores: dict         # {pyramid_id: score} 各金字塔评分
    source_health_score: int     # 信息源整体健康评分 0-100
    content_coverage_score: int  # 内容覆盖度评分 0-100
    
    # 统计数据
    hotspot_distribution: dict   # {status: count} 热点分布
    approval_backlog: dict       # {count: int, avg_wait_hours: float}
    crawl_stats: dict            # {success_rate: float, new_count: int}
    
    # 问题列表
    issues: list[dict]           # [{type, severity, description, suggestion}]
    
    created_at: datetime
```

### 策略调整记录 (Strategy_Adjustment)

```python
class StrategyAdjustment(Base):
    __tablename__ = "strategy_adjustments"
    
    id: str                      # UUID
    source_id: str               # 信息源 ID
    adjustment_type: str         # frequency/timeout/retry/filter
    
    # 调整详情
    old_value: dict              # 调整前参数
    new_value: dict              # 调整后参数
    reason: str                  # 调整原因
    expected_effect: str         # 预期效果
    
    # 审批
    requires_approval: bool      # 是否需要审批
    proposal_id: str | None      # 关联的变更提案 ID
    
    created_at: datetime
    applied_at: datetime | None  # 生效时间
```

### 定时任务 (Scheduled_Task)

```python
class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    
    id: str                      # UUID
    task_name: str               # 任务名称
    task_type: str               # crawl/health_check/health_detection/hotspot_update/drift_detection
    
    # 调度配置
    cron_expression: str         # Cron 表达式
    is_active: bool              # 是否启用
    
    # 执行状态
    last_run_at: datetime | None # 上次执行时间
    next_run_at: datetime | None # 下次执行时间
    is_running: bool             # 是否正在执行
    
    # 重试配置
    max_retries: int             # 最大重试次数
    retry_delay_seconds: int     # 重试间隔（秒）
    
    created_at: datetime
    updated_at: datetime
```

### 任务执行记录 (Task_Execution)

```python
class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id: str                      # UUID
    task_id: str                 # 定时任务 ID
    
    status: str                  # running/success/failed/retrying
    started_at: datetime         # 开始时间
    ended_at: datetime | None    # 结束时间
    duration_seconds: float | None  # 耗时（秒）
    
    result: dict | None          # 执行结果
    error_message: str | None    # 错误信息
    retry_count: int             # 重试次数
    
    created_at: datetime
```

### 配置变更历史 (Config_History)

```python
class ConfigHistory(Base):
    __tablename__ = "config_history"
    
    id: str                      # UUID
    config_key: str              # 配置键
    old_value: str | None        # 旧值
    new_value: str               # 新值
    changed_by: str              # 变更者
    
    created_at: datetime
```

## 组件接口设计

### 系统健康检测器

```python
# services/evolution/health_detector.py
from dataclasses import dataclass

@dataclass
class DimensionScore:
    dimension: str              # 维度名称
    score: int                  # 评分 0-100
    weight: float               # 权重
    details: dict               # 详细信息
    issues: list[dict]          # 发现的问题

@dataclass
class HealthDetectionResult:
    overall_score: int          # 整体评分 0-100
    dimension_scores: list[DimensionScore]
    issues: list[dict]          # 所有问题列表
    triggered_actions: list[str]  # 触发的优化动作

class HealthDetector:
    # 维度权重配置
    DIMENSION_WEIGHTS = {
        "pyramid_structure": 0.25,
        "source_health": 0.25,
        "content_coverage": 0.20,
        "hotspot_distribution": 0.15,
        "approval_backlog": 0.15,
    }
    
    async def run_full_detection(self) -> HealthDetectionResult:
        """执行全面健康检测"""
        pass
    
    async def evaluate_pyramid_structure(self, pyramid_id: str) -> DimensionScore:
        """评估金字塔结构平衡性"""
        pass
    
    async def evaluate_source_health(self) -> DimensionScore:
        """评估信息源整体健康状况"""
        pass
    
    async def evaluate_hotspot_distribution(self) -> DimensionScore:
        """评估热点生命周期分布"""
        pass
    
    async def evaluate_content_coverage(self) -> DimensionScore:
        """评估内容更新频率和覆盖度"""
        pass
    
    async def evaluate_approval_backlog(self) -> DimensionScore:
        """评估审批队列积压情况"""
        pass
    
    def calculate_overall_score(self, dimension_scores: list[DimensionScore]) -> int:
        """计算加权平均整体评分"""
        pass
    
    async def save_report(self, result: HealthDetectionResult) -> HealthReport:
        """保存健康报告"""
        pass
```

### 金字塔重构建议器

```python
# services/evolution/restructure_advisor.py
@dataclass
class StructureIssue:
    issue_type: str             # content_overload/empty_node/deep_hierarchy/too_many_siblings/naming_inconsistency
    node_id: str
    pyramid_id: str
    severity: str               # low/medium/high
    details: dict

@dataclass
class RestructureProposal:
    issue: StructureIssue
    proposal_type: str          # split_node/delete_node/merge_nodes/flatten/group/rename
    reasoning: str              # 重构理由
    expected_effect: str        # 预期效果
    risk_assessment: str        # 风险评估
    payload: dict               # 提案具体内容

class RestructureAdvisor:
    # 可配置阈值
    CONTENT_OVERLOAD_THRESHOLD = 50
    EMPTY_NODE_DAYS = 30
    MAX_DEPTH = 5
    MAX_SIBLINGS = 10
    
    def __init__(self, config_service: ConfigurationService, ai_client: SiliconFlowClient):
        self.config_service = config_service
        self.ai_client = ai_client
    
    async def analyze_pyramid(self, pyramid_id: str) -> list[StructureIssue]:
        """分析金字塔结构问题"""
        pass
    
    async def detect_content_overload(self, pyramid_id: str) -> list[StructureIssue]:
        """检测内容过载节点"""
        pass
    
    async def detect_empty_nodes(self, pyramid_id: str) -> list[StructureIssue]:
        """检测长期无内容节点"""
        pass
    
    async def detect_deep_hierarchy(self, pyramid_id: str) -> list[StructureIssue]:
        """检测层级过深"""
        pass
    
    async def detect_too_many_siblings(self, pyramid_id: str) -> list[StructureIssue]:
        """检测同级节点过多"""
        pass
    
    async def generate_proposals(self, issues: list[StructureIssue]) -> list[ChangeProposal]:
        """为检测到的问题生成重构提案"""
        pass
```

### 热点生命周期管理器

```python
# services/evolution/hotspot_manager.py
@dataclass
class HotspotTransition:
    hotspot_id: str
    old_status: str
    new_status: str
    trigger_condition: str

class HotspotManager:
    # 状态转换阈值
    EMERGING_THRESHOLD = 5          # 7 天内提及次数
    GROWTH_SLOWDOWN_RATE = 0.10     # 增长率低于 10% 视为放缓
    COOLING_DECLINE_DAYS = 14       # 连续下降天数
    ARCHIVE_INACTIVE_DAYS = 30      # 无更新天数
    
    # 优先级权重映射
    PRIORITY_WEIGHTS = {
        "emerging": 0.8,
        "trending": 1.0,
        "mature": 0.6,
        "cooling": 0.3,
        "archived": 0.1,
    }
    
    async def update_lifecycle(self) -> list[HotspotTransition]:
        """更新所有热点的生命周期状态"""
        pass
    
    async def detect_emerging_topics(self) -> list[Hotspot]:
        """检测新兴话题"""
        pass
    
    async def evaluate_transitions(self, hotspot: Hotspot) -> HotspotTransition | None:
        """评估单个热点的状态转换"""
        pass
    
    async def apply_transition(self, transition: HotspotTransition) -> None:
        """应用状态转换"""
        pass
    
    async def adjust_display_priority(self, hotspot: Hotspot) -> None:
        """调整展示优先级"""
        pass
    
    async def manual_adjust(self, hotspot_id: str, new_status: str, operator: str) -> Hotspot:
        """手动调整热点状态"""
        pass
    
    async def get_lifecycle_trajectory(self, hotspot_id: str) -> list[HotspotEvent]:
        """获取热点生命周期轨迹"""
        pass
    
    async def get_distribution(self) -> dict[str, int]:
        """获取热点状态分布"""
        pass
```

### 概念漂移检测器

```python
# services/evolution/concept_drift_detector.py
@dataclass
class DriftDetection:
    term: str
    old_context: str
    new_context: str
    similarity_score: float
    drift_evidence: list[str]
    suggested_new_definition: str

class ConceptDriftDetector:
    SIMILARITY_THRESHOLD = 0.7
    
    def __init__(self, ai_client: SiliconFlowClient):
        self.ai_client = ai_client
    
    async def run_detection(self) -> list[DriftDetection]:
        """执行概念漂移检测"""
        pass
    
    async def extract_term_context(self, term: str, content_ids: list[str]) -> str:
        """提取术语的当前使用上下文"""
        pass
    
    async def compare_contexts(self, term: str, old_context: str, new_context: str) -> float:
        """比较上下文相似度"""
        pass
    
    async def generate_drift_proposals(self, detections: list[DriftDetection]) -> list[ChangeProposal]:
        """为检测到的漂移生成变更提案"""
        pass
    
    async def save_definition_version(self, term: str, definition: str, context_examples: list[str]) -> ConceptDefinition:
        """保存术语定义版本"""
        pass
    
    async def get_definition_history(self, term: str) -> list[ConceptDefinition]:
        """获取术语定义历史"""
        pass
```

### 抓取策略优化器

```python
# services/evolution/strategy_optimizer.py
@dataclass
class StrategyRecommendation:
    source_id: str
    adjustment_type: str        # frequency/timeout/retry/filter
    old_value: dict
    new_value: dict
    reason: str
    expected_effect: str
    requires_approval: bool     # 调整幅度超过 50% 时需要审批

class StrategyOptimizer:
    FREQUENCY_DEVIATION_THRESHOLD = 0.30    # 频率偏差阈值
    TIMEOUT_WARNING_RATIO = 0.80            # 超时预警比例
    SUCCESS_RATE_THRESHOLD = 0.70           # 成功率阈值
    QUALITY_SCORE_THRESHOLD = 50            # 质量分数阈值
    MAJOR_CHANGE_THRESHOLD = 0.50           # 重大变更阈值
    
    async def analyze_all_sources(self) -> list[StrategyRecommendation]:
        """分析所有信息源并生成策略建议"""
        pass
    
    async def analyze_frequency(self, source_id: str) -> StrategyRecommendation | None:
        """分析抓取频率是否需要调整"""
        pass
    
    async def analyze_timeout(self, source_id: str) -> StrategyRecommendation | None:
        """分析超时设置是否需要调整"""
        pass
    
    async def analyze_success_rate(self, source_id: str) -> StrategyRecommendation | None:
        """分析成功率并调整策略"""
        pass
    
    async def analyze_quality(self, source_id: str) -> StrategyRecommendation | None:
        """分析内容质量并调整过滤规则"""
        pass
    
    async def apply_recommendation(self, recommendation: StrategyRecommendation) -> StrategyAdjustment:
        """应用策略建议（小幅调整直接应用，大幅调整生成提案）"""
        pass
    
    async def record_adjustment(self, adjustment: StrategyAdjustment) -> None:
        """记录策略调整"""
        pass
```

### 定时任务调度服务

```python
# services/scheduler/scheduler_service.py
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    CRAWL = "crawl"
    HEALTH_CHECK = "health_check"
    HEALTH_DETECTION = "health_detection"
    HOTSPOT_UPDATE = "hotspot_update"
    DRIFT_DETECTION = "drift_detection"

@dataclass
class TaskStatus:
    task_id: str
    task_name: str
    task_type: str
    is_active: bool
    is_running: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    success_rate: float

class SchedulerService:
    MAX_RETRIES = 3
    
    async def register_task(self, task_name: str, task_type: TaskType, cron_expression: str) -> ScheduledTask:
        """注册定时任务"""
        pass
    
    async def start(self) -> None:
        """启动调度器"""
        pass
    
    async def stop(self) -> None:
        """停止调度器"""
        pass
    
    async def trigger_task(self, task_id: str) -> TaskExecution:
        """手动触发任务"""
        pass
    
    async def pause_task(self, task_id: str) -> None:
        """暂停任务"""
        pass
    
    async def resume_task(self, task_id: str) -> None:
        """恢复任务"""
        pass
    
    async def get_task_status(self, task_id: str) -> TaskStatus:
        """获取任务状态"""
        pass
    
    async def list_tasks(self) -> list[TaskStatus]:
        """列出所有任务"""
        pass
    
    async def get_execution_history(
        self,
        task_id: str | None = None,
        task_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        size: int = 20
    ) -> list[TaskExecution]:
        """获取执行历史"""
        pass
    
    async def execute_with_retry(self, task: ScheduledTask, func: callable) -> TaskExecution:
        """带重试的任务执行"""
        pass
    
    async def acquire_lock(self, task_id: str) -> bool:
        """获取任务锁（防止并发执行）"""
        pass
    
    async def release_lock(self, task_id: str) -> None:
        """释放任务锁"""
        pass
```

### 配置管理服务

```python
# services/config/configuration_service.py
from dataclasses import dataclass

@dataclass
class ConfigItem:
    key: str
    value: str
    category: str               # crawl/validation/health/ai/retry/restructure
    description: str
    value_type: str             # int/float/str/bool/json
    default_value: str
    validation_rule: str | None  # 验证规则（正则或范围）

class ConfigurationService:
    # 默认配置
    DEFAULTS = {
        # 抓取配置
        "crawl.default_frequency_minutes": "60",
        "crawl.max_concurrent": "10",
        "crawl.default_timeout_seconds": "30",
        
        # 校验配置
        "validation.quality_threshold": "60",
        "validation.confidence_threshold": "0.8",
        
        # 健康度配置
        "health.pyramid_balance_weight": "0.25",
        "health.source_health_weight": "0.25",
        "health.content_coverage_weight": "0.20",
        "health.hotspot_weight": "0.15",
        "health.approval_weight": "0.15",
        
        # AI 配置
        "ai.model_name": "deepseek-chat",
        "ai.temperature": "0.7",
        "ai.max_tokens": "2000",
        
        # 重试配置
        "retry.max_retries": "3",
        "retry.base_delay_seconds": "5",
        
        # 重构阈值
        "restructure.content_overload_threshold": "50",
        "restructure.empty_node_days": "30",
        "restructure.max_depth": "5",
        "restructure.max_siblings": "10",
    }
    
    def __init__(self):
        self._config_cache: dict[str, str] = {}
        self._watchers: list[callable] = []
    
    async def load(self) -> None:
        """加载配置（环境变量 > 配置文件 > 默认值）"""
        pass
    
    async def get(self, key: str, default: str | None = None) -> str:
        """获取配置值"""
        pass
    
    async def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值"""
        pass
    
    async def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置值"""
        pass
    
    async def set(self, key: str, value: str, changed_by: str) -> None:
        """设置配置值（带验证和历史记录）"""
        pass
    
    async def validate(self, key: str, value: str) -> bool:
        """验证配置值"""
        pass
    
    async def get_all(self, category: str | None = None) -> list[ConfigItem]:
        """获取所有配置项"""
        pass
    
    async def get_history(self, key: str | None = None, limit: int = 50) -> list[ConfigHistory]:
        """获取配置变更历史"""
        pass
    
    def on_change(self, callback: callable) -> None:
        """注册配置变更回调"""
        pass
    
    async def reload(self) -> None:
        """热更新配置"""
        pass
```

## API 端点

```python
# 健康报告
GET  /api/health/report                    # 获取最新健康报告
GET  /api/health/report/history            # 获取历史健康报告列表
POST /api/health/detect                    # 手动触发健康检测
GET  /api/health/pyramid/{pyramid_id}      # 获取单个金字塔健康详情
GET  /api/health/sources                   # 获取信息源健康汇总
GET  /api/health/hotspots                  # 获取热点分布

# 热点管理
GET  /api/hotspots                         # 获取热点列表
GET  /api/hotspots/{id}                    # 获取热点详情
GET  /api/hotspots/{id}/trajectory         # 获取热点生命周期轨迹
PUT  /api/hotspots/{id}/status             # 手动调整热点状态

# 概念漂移
GET  /api/drift/detections                 # 获取漂移检测结果
GET  /api/drift/terms/{term}/history       # 获取术语定义历史
POST /api/drift/detect                     # 手动触发漂移检测

# 策略调整
GET  /api/strategy/adjustments             # 获取策略调整记录
GET  /api/strategy/recommendations         # 获取当前策略建议

# 定时任务
GET  /api/scheduler/tasks                  # 获取任务列表
GET  /api/scheduler/tasks/{id}             # 获取任务详情
POST /api/scheduler/tasks/{id}/trigger     # 手动触发任务
PUT  /api/scheduler/tasks/{id}/pause       # 暂停任务
PUT  /api/scheduler/tasks/{id}/resume      # 恢复任务
GET  /api/scheduler/executions             # 获取执行历史

# 系统配置
GET  /api/config                           # 获取所有配置
GET  /api/config/{key}                     # 获取单个配置
PUT  /api/config/{key}                     # 修改配置
GET  /api/config/history                   # 获取配置变更历史
```

## Prompt 模板

### 金字塔结构分析 Prompt

```python
PYRAMID_STRUCTURE_ANALYSIS_PROMPT = """
你是一个知识结构分析专家。请分析以下金字塔节点结构，识别潜在的结构问题。

金字塔名称：{pyramid_name}
节点结构：
{node_tree_json}

请分析以下方面：
1. 是否有节点内容过多需要拆分
2. 是否有节点长期无内容需要删除或合并
3. 层级深度是否合理
4. 同级节点数量是否过多
5. 节点命名是否一致

请返回 JSON 格式：
{{
    "issues": [
        {{
            "type": "content_overload|empty_node|deep_hierarchy|too_many_siblings|naming_inconsistency",
            "node_id": "受影响节点 ID",
            "severity": "low|medium|high",
            "description": "问题描述",
            "suggestion": "建议操作"
        }}
    ],
    "overall_assessment": "整体评估说明"
}}
"""
```

### 概念漂移检测 Prompt

```python
CONCEPT_DRIFT_DETECTION_PROMPT = """
你是一个 AI 领域术语专家。请比较以下术语在不同时期的使用上下文，判断是否发生了概念漂移。

术语：{term}

历史上下文（{old_period}）：
{old_context}

当前上下文（{new_period}）：
{new_context}

请返回 JSON 格式：
{{
    "similarity_score": 0.0-1.0,
    "drift_detected": true|false,
    "drift_type": "meaning_shift|scope_change|new_usage|none",
    "evidence": ["证据1", "证据2"],
    "old_definition": "旧定义",
    "new_definition": "新定义（如果发生漂移）",
    "reasoning": "分析推理过程"
}}
"""
```

### 策略优化建议 Prompt

```python
STRATEGY_OPTIMIZATION_PROMPT = """
你是一个信息抓取策略专家。请根据以下信息源的运行数据，给出策略优化建议。

信息源名称：{source_name}
信息源类型：{source_type}
当前配置：{current_config}

运行数据（近 7 天）：
- 抓取成功率：{success_rate}%
- 平均响应时间：{avg_response_time}ms
- 实际更新频率：每 {actual_frequency} 分钟
- 配置抓取频率：每 {config_frequency} 分钟
- 平均内容质量分数：{avg_quality_score}

请返回 JSON 格式：
{{
    "recommendations": [
        {{
            "type": "frequency|timeout|retry|filter",
            "current_value": "当前值",
            "suggested_value": "建议值",
            "reason": "调整原因",
            "expected_effect": "预期效果",
            "change_magnitude": 0.0-1.0
        }}
    ],
    "overall_assessment": "整体评估"
}}
"""
```


## 正确性属性

*正确性属性是系统应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 健康评分范围不变量
*For any* 健康检测结果，所有维度评分（金字塔结构、信息源健康、内容覆盖度）和系统整体评分必须在 0-100 范围内，且整体评分等于各维度评分的加权平均值（误差不超过 1）。
**Validates: Requirements 1.1, 1.2, 1.4, 1.9**

### Property 2: 健康问题触发一致性
*For any* 健康检测结果，如果某维度评分低于配置的阈值，则问题报告中必须包含该维度的问题描述和改进建议。
**Validates: Requirements 1.6**

### Property 3: 热点分布统计完整性
*For any* 热点分布统计结果，各状态的数量之和必须等于系统中所有热点的总数。
**Validates: Requirements 1.3**

### Property 4: 审批积压统计正确性
*For any* 审批积压评估结果，积压数量必须等于数据库中状态为 pending 或 queued 的提案数量，平均等待时间必须为非负数。
**Validates: Requirements 1.5**

### Property 5: 重构提案触发正确性
*For any* 金字塔结构分析结果，当节点内容数量超过阈值时必须生成拆分提案，当节点无内容超过指定天数时必须生成删除/合并提案，当层级深度超过阈值时必须生成扁平化提案，当同级节点数超过阈值时必须生成分组提案。
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 6: 重构提案内容完整性
*For any* 生成的重构提案，必须包含非空的重构理由（reasoning）、预期效果（expected_effect）和风险评估（risk_assessment）字段。
**Validates: Requirements 2.6**

### Property 7: 热点生命周期状态转换正确性
*For any* 热点话题，给定其当前状态和频率指标，状态转换必须遵循定义的生命周期规则：emerging→trending（频率持续增长）→mature（增长放缓）→cooling（频率下降）→archived（长期无更新）。不允许跳过中间状态的自动转换。
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 8: 热点优先级权重单调性
*For any* 热点状态变化，展示优先级权重必须满足：trending > emerging > mature > cooling > archived。
**Validates: Requirements 3.6**

### Property 9: 热点生命周期轨迹完整性
*For any* 经历过状态转换的热点，其生命周期轨迹必须包含所有状态变更事件，且事件按时间顺序排列。
**Validates: Requirements 3.7**

### Property 10: 概念漂移检测阈值一致性
*For any* 术语上下文比较结果，当语义相似度低于阈值（0.7）时必须标记为潜在概念漂移，当相似度高于或等于阈值时不应标记为漂移。
**Validates: Requirements 4.2**

### Property 11: 概念漂移提案完整性
*For any* 检测到的概念漂移，生成的 Change_Proposal 必须包含旧定义、新定义和漂移证据，且关联的节点描述更新建议。
**Validates: Requirements 4.3, 4.4, 4.6**

### Property 12: 术语定义版本链完整性
*For any* 关键术语，其定义版本列表必须按版本号升序排列，且当前版本（is_current=true）有且仅有一个。
**Validates: Requirements 4.5**

### Property 13: 策略自适应触发正确性
*For any* 信息源运行数据，当实际更新频率偏差超过 30% 时必须调整抓取频率，当响应时间超过超时的 80% 时必须增加超时，当成功率连续 3 天低于 70% 时必须调整策略，当质量分数连续 7 天低于 50 时必须调整过滤规则。
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 14: 重大策略变更审批要求
*For any* 策略调整，当调整幅度超过原配置的 50% 时，必须生成 Change_Proposal 而非直接应用，requires_approval 字段必须为 true。
**Validates: Requirements 5.5**

### Property 15: 策略调整记录完整性
*For any* 策略调整操作，必须记录调整原因（非空）、调整前参数、调整后参数和预期效果。
**Validates: Requirements 5.6**

### Property 16: 任务执行记录完整性
*For any* 定时任务执行，必须记录开始时间、结束时间（或 None 表示仍在运行）和执行结果，且 duration_seconds 等于 ended_at - started_at。
**Validates: Requirements 7.2**

### Property 17: 任务重试策略正确性
*For any* 失败的定时任务，重试次数不超过配置的最大重试次数，且重试间隔遵循指数退避策略。
**Validates: Requirements 7.3**

### Property 18: 任务暂停/恢复一致性
*For any* 被暂停的任务，在暂停期间不应产生新的执行记录；恢复后应重新开始调度。
**Validates: Requirements 7.5**

### Property 19: 任务并发执行防护
*For any* 定时任务，如果该任务当前正在执行（is_running=true），新的执行请求应被阻止并返回错误。
**Validates: Requirements 7.6**

### Property 20: 配置验证拒绝无效值
*For any* 配置修改请求，如果值不符合验证规则（如负数的阈值、超出范围的权重），修改应被拒绝且配置保持不变。
**Validates: Requirements 8.4**

### Property 21: 配置变更历史完整性
*For any* 配置修改操作，必须在 config_history 表中创建一条记录，包含配置键、旧值、新值和变更者。
**Validates: Requirements 8.5**

### Property 22: 配置热更新往返一致性
*For any* 配置修改操作，修改后立即读取该配置应返回新值，无需重启服务。
**Validates: Requirements 8.6**


## 错误处理

### API 错误响应格式

```python
# 新增错误码
ERROR_CODES = {
    # 健康检测错误
    "HEALTH_DETECTION_FAILED": "健康检测执行失败",
    "HEALTH_REPORT_NOT_FOUND": "健康报告不存在",
    
    # 热点管理错误
    "HOTSPOT_NOT_FOUND": "热点话题不存在",
    "INVALID_HOTSPOT_STATUS": "无效的热点状态",
    "HOTSPOT_TRANSITION_INVALID": "无效的状态转换",
    
    # 概念漂移错误
    "DRIFT_DETECTION_FAILED": "概念漂移检测失败",
    "TERM_NOT_FOUND": "术语不存在",
    
    # 策略优化错误
    "STRATEGY_ANALYSIS_FAILED": "策略分析失败",
    "STRATEGY_APPLY_FAILED": "策略应用失败",
    
    # 定时任务错误
    "TASK_NOT_FOUND": "定时任务不存在",
    "TASK_ALREADY_RUNNING": "任务正在执行中",
    "TASK_PAUSED": "任务已暂停",
    "TASK_LOCK_FAILED": "获取任务锁失败",
    
    # 配置错误
    "CONFIG_KEY_NOT_FOUND": "配置项不存在",
    "CONFIG_VALIDATION_FAILED": "配置值验证失败",
    "CONFIG_READONLY": "该配置项为只读",
}
```

### 错误处理策略

| 错误类型 | 处理方式 | HTTP 状态码 |
|---------|---------|------------|
| 健康检测失败 | 记录错误，返回上次成功报告 | 500 |
| 热点不存在 | 返回 404 | 404 |
| 无效状态转换 | 返回错误说明 | 400 |
| 任务正在执行 | 返回冲突错误 | 409 |
| 配置验证失败 | 返回验证错误详情 | 422 |
| AI 服务不可用 | 重试后降级处理 | 503 |
| 任务锁获取失败 | 返回冲突错误 | 409 |

## 测试策略

### 单元测试

- 健康评分计算逻辑（各维度评分、加权平均）
- 重构问题检测逻辑（阈值判断、提案生成）
- 热点状态转换逻辑（状态机规则）
- 概念漂移检测逻辑（相似度阈值判断）
- 策略优化逻辑（偏差计算、调整幅度判断）
- 定时任务调度逻辑（锁机制、重试策略）
- 配置验证逻辑（类型检查、范围验证）

### 属性测试

使用 Hypothesis 库进行属性测试，每个属性测试运行至少 100 次迭代。

测试标签格式：`Feature: ai-radar-iteration-4, Property N: {property_text}`

```python
from hypothesis import given, strategies as st

# 健康评分策略
score_strategy = st.integers(min_value=0, max_value=100)
weight_strategy = st.floats(min_value=0.0, max_value=1.0)

# 热点频率策略
frequency_strategy = st.integers(min_value=0, max_value=1000)
growth_rate_strategy = st.floats(min_value=-1.0, max_value=10.0)

# 配置值策略
config_value_strategy = st.one_of(
    st.integers(min_value=0, max_value=10000).map(str),
    st.floats(min_value=0.0, max_value=1.0).map(str),
    st.text(min_size=1, max_size=100)
)

# 策略偏差策略
deviation_strategy = st.floats(min_value=0.0, max_value=2.0)
```

### 集成测试

- 完整健康检测流程（检测→报告→触发优化）
- 热点生命周期完整流转（emerging→trending→mature→cooling→archived）
- 策略自适应流程（分析→建议→应用/审批）
- 定时任务调度流程（注册→执行→重试→记录）
- 配置热更新流程（修改→验证→生效→历史记录）

### Mock 策略

- AI 服务使用 mock 响应进行单元测试
- 定时任务使用加速时钟进行测试
- 集成测试使用真实 AI 服务（限制调用次数）

### 测试数据生成策略

```python
from hypothesis import strategies as st

# 金字塔结构策略（用于重构检测测试）
def pyramid_structure_strategy(max_depth=6, max_children=15):
    return st.recursive(
        st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'content_count': st.integers(min_value=0, max_value=100),
            'last_content_date': st.datetimes(),
        }),
        lambda children: st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'content_count': st.integers(min_value=0, max_value=100),
            'last_content_date': st.datetimes(),
            'children': st.lists(children, max_size=max_children),
        }),
        max_leaves=max_depth
    )

# 热点话题策略
hotspot_strategy = st.fixed_dictionaries({
    'topic_name': st.text(min_size=1, max_size=100),
    'status': st.sampled_from(['emerging', 'trending', 'mature', 'cooling', 'archived']),
    'recent_7d_count': st.integers(min_value=0, max_value=1000),
    'previous_7d_count': st.integers(min_value=0, max_value=1000),
    'growth_rate': st.floats(min_value=-1.0, max_value=10.0),
})

# 信息源运行数据策略
source_metrics_strategy = st.fixed_dictionaries({
    'success_rate': st.floats(min_value=0.0, max_value=1.0),
    'avg_response_time_ms': st.integers(min_value=100, max_value=60000),
    'actual_frequency_minutes': st.integers(min_value=1, max_value=1440),
    'config_frequency_minutes': st.integers(min_value=1, max_value=1440),
    'avg_quality_score': st.integers(min_value=0, max_value=100),
})
```
