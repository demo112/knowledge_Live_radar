# 设计文档 - 迭代 3：用户输入与金字塔进化

## 概述

本设计文档描述 AI Radar 系统迭代 3 的技术实现方案。迭代 3 的目标是实现用户多模态输入、AI 驱动的概念提取、变更提案系统和人类审批机制。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户输入层                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  URL 输入    │  │  文件上传    │  │  文本输入    │  │  批量输入    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          └─────────────────┴─────────────────┴─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              内容处理层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Input_Processor                                │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │ URL 抓取   │  │ PDF 解析   │  │ Word 解析  │  │ OCR 识别   │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              概念分析层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Concept_Extractor                              │  │
│  │  ┌────────────────────┐  ┌────────────────────┐                      │  │
│  │  │  AI 概念识别       │  │  概念关系分析      │                      │  │
│  │  └────────────────────┘  └────────────────────┘                      │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Concept_Matcher                                │  │
│  │  ┌────────────────────┐  ┌────────────────────┐                      │  │
│  │  │  节点匹配          │  │  同义词扩展        │                      │  │
│  │  └────────────────────┘  └────────────────────┘                      │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              提案生成层                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Proposal_Generator                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │ 添加节点 │  │ 重命名   │  │ 拆分     │  │ 合并     │  │ 关联   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              审批执行层                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │ Approval_Queue │  │ Impact_Analyzer│  │Decision_Executor│               │
│  │    _Manager    │  │                │  │                │                │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                │
│          └───────────────────┼───────────────────┘                          │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Snapshot_Manager                               │  │
│  │  ┌────────────────────┐  ┌────────────────────┐                      │  │
│  │  │  状态快照          │  │  回滚执行          │                      │  │
│  │  └────────────────────┘  └────────────────────┘                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 变更提案状态机

```
                    ┌──────────────┐
                    │   pending    │ ← 新创建
                    └──────┬───────┘
                           │ 进入审批队列
                           ▼
                    ┌──────────────┐
                    │   queued     │
                    └──────┬───────┘
                           │ 管理员查看
              ┌────────────┼────────────┐
              ▼            ▼            ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │   approved   │ │   rejected   │ │   modified   │
      └──────┬───────┘ └──────────────┘ └──────┬───────┘
             │                                  │
             │ 执行变更                         │ 创建新版本
             ▼                                  ▼
      ┌──────────────┐                  ┌──────────────┐
      │   executed   │                  │   pending    │ (新版本)
      └──────┬───────┘                  └──────────────┘
             │ 回滚
             ▼
      ┌──────────────┐
      │  rolled_back │
      └──────────────┘
```


## 目录结构（新增）

```
backend/
├── app/
│   ├── services/
│   │   ├── input/                    # 输入处理
│   │   │   ├── __init__.py
│   │   │   ├── input_processor.py    # 输入处理器
│   │   │   ├── file_parser.py        # 文件解析器
│   │   │   └── batch_processor.py    # 批量处理器
│   │   ├── concept/                  # 概念处理
│   │   │   ├── __init__.py
│   │   │   ├── concept_extractor.py  # 概念提取器
│   │   │   ├── concept_matcher.py    # 概念匹配器
│   │   │   └── synonym_manager.py    # 同义词管理
│   │   ├── proposal/                 # 提案管理
│   │   │   ├── __init__.py
│   │   │   ├── proposal_generator.py # 提案生成器
│   │   │   ├── approval_queue.py     # 审批队列
│   │   │   ├── impact_analyzer.py    # 影响分析器
│   │   │   ├── decision_executor.py  # 决策执行器
│   │   │   └── priority_calculator.py # 优先级计算
│   │   ├── snapshot/                 # 快照管理
│   │   │   ├── __init__.py
│   │   │   └── snapshot_manager.py   # 快照管理器
│   │   ├── contribution/             # 贡献追踪
│   │   │   ├── __init__.py
│   │   │   └── contribution_tracker.py
│   │   └── notification/             # 通知服务
│   │       ├── __init__.py
│   │       └── notification_service.py
│   ├── api/
│   │   ├── input.py                  # 输入 API
│   │   ├── proposals.py              # 提案 API
│   │   ├── approvals.py              # 审批 API
│   │   ├── contributions.py          # 贡献 API
│   │   └── snapshots.py              # 快照 API
│   └── models/
│       ├── change_proposal.py        # 变更提案模型
│       ├── state_snapshot.py         # 状态快照模型
│       ├── contribution.py           # 贡献记录模型
│       ├── synonym_mapping.py        # 同义词映射模型
│       ├── batch_task.py             # 批量任务模型
│       └── notification.py           # 通知模型

frontend/
├── src/
│   ├── app/
│   │   ├── approval/                 # 审批中心
│   │   │   ├── page.tsx              # 审批队列页面
│   │   │   └── [id]/page.tsx         # 提案详情页面
│   │   ├── input/                    # 内容输入
│   │   │   └── page.tsx              # 输入页面
│   │   ├── history/                  # 变更历史
│   │   │   └── page.tsx              # 历史页面
│   │   └── contributions/            # 贡献记录
│   │       └── page.tsx              # 贡献页面
│   └── components/
│       ├── approval/                 # 审批组件
│       │   ├── ProposalList.tsx
│       │   ├── ProposalCard.tsx
│       │   ├── ProposalDetail.tsx
│       │   ├── ImpactAnalysis.tsx
│       │   └── ApprovalActions.tsx
│       ├── input/                    # 输入组件
│       │   ├── InputSelector.tsx
│       │   ├── UrlInput.tsx
│       │   ├── FileUpload.tsx
│       │   ├── TextInput.tsx
│       │   └── ConceptPreview.tsx
│       └── history/                  # 历史组件
│           ├── ChangeTimeline.tsx
│           ├── ChangeDetail.tsx
│           └── RollbackDialog.tsx
```


## 数据模型

### 变更提案 (Change_Proposal)

```python
class ChangeProposal(Base):
    __tablename__ = "change_proposals"
    
    id: str                      # UUID
    proposal_type: str           # add_node/rename_node/split_node/merge_nodes/add_relation
    status: str                  # pending/queued/approved/rejected/modified/executed/rolled_back
    priority: int                # 优先级分数 1-100
    
    # 提案内容（JSON）
    payload: dict                # 提案具体内容，结构因类型而异
    
    # 来源信息
    source_type: str             # user_input/system_discovery/ai_suggestion
    source_content_id: str | None  # 触发提案的内容 ID
    contribution_id: str | None  # 关联的贡献记录 ID
    
    # AI 推理
    ai_reasoning: str            # AI 生成提案的推理过程
    confidence: float            # 置信度 0-1
    
    # 影响分析
    impact_analysis: dict | None # 影响分析结果 JSON
    
    # 审批信息
    reviewed_by: str | None      # 审批人
    reviewed_at: datetime | None # 审批时间
    review_comment: str | None   # 审批意见
    
    # 版本控制
    version: int                 # 版本号
    parent_proposal_id: str | None  # 父提案 ID（修改时）
    
    # 执行信息
    executed_at: datetime | None # 执行时间
    snapshot_id: str | None      # 关联的快照 ID
    
    created_at: datetime
    updated_at: datetime
```

### 提案 Payload 结构

```python
# 添加节点提案
AddNodePayload = {
    "node_name": str,           # 新节点名称
    "node_description": str,    # 节点描述
    "parent_node_id": str,      # 父节点 ID
    "pyramid_id": str,          # 所属金字塔 ID
    "suggested_position": int,  # 建议排序位置
    "related_concepts": list[str]  # 相关概念列表
}

# 重命名节点提案
RenameNodePayload = {
    "node_id": str,             # 目标节点 ID
    "old_name": str,            # 原名称
    "new_name": str,            # 新名称
    "reason": str               # 重命名原因
}

# 拆分节点提案
SplitNodePayload = {
    "node_id": str,             # 目标节点 ID
    "original_name": str,       # 原节点名称
    "new_nodes": list[{         # 拆分后的新节点
        "name": str,
        "description": str,
        "content_ids": list[str]  # 分配到该节点的内容
    }],
    "reason": str               # 拆分原因
}

# 合并节点提案
MergeNodesPayload = {
    "node_ids": list[str],      # 待合并节点 ID 列表
    "merged_name": str,         # 合并后名称
    "merged_description": str,  # 合并后描述
    "target_parent_id": str,    # 合并后的父节点
    "reason": str               # 合并原因
}

# 建立关联提案
AddRelationPayload = {
    "source_node_id": str,      # 源节点 ID
    "target_node_id": str,      # 目标节点 ID
    "relation_type": str,       # 关联类型: related/depends_on/extends
    "reason": str               # 关联原因
}
```


### 状态快照 (State_Snapshot)

```python
class StateSnapshot(Base):
    __tablename__ = "state_snapshots"
    
    id: str                      # UUID
    proposal_id: str             # 关联的提案 ID
    snapshot_type: str           # pre_change/post_change
    
    # 快照数据
    affected_nodes: dict         # 受影响节点的完整数据
    affected_mappings: dict      # 受影响的映射关系
    affected_contents: dict      # 受影响内容的分类信息
    
    # 元数据
    created_at: datetime
    expires_at: datetime         # 过期时间（30天后）
    is_valid: bool               # 快照是否有效
    checksum: str                # 数据校验和
```

### 用户贡献 (Contribution)

```python
class Contribution(Base):
    __tablename__ = "contributions"
    
    id: str                      # UUID
    user_id: str | None          # 用户 ID（匿名时为 None）
    input_type: str              # url/pdf/word/markdown/image/text
    
    # 输入内容
    original_input: str          # 原始输入（URL 或文件路径或文本）
    extracted_content: str       # 提取的文本内容
    
    # 处理结果
    status: str                  # pending/processing/completed/failed/adopted/rejected
    extracted_concepts: list[dict]  # 提取的概念列表
    
    # 关联信息
    proposal_ids: list[str]      # 触发的提案 ID 列表
    content_id: str | None       # 创建的内容 ID
    
    # 审核信息
    rejection_reason: str | None # 拒绝原因
    
    created_at: datetime
    updated_at: datetime
```

### 同义词映射 (Synonym_Mapping)

```python
class SynonymMapping(Base):
    __tablename__ = "synonym_mappings"
    
    id: str                      # UUID
    canonical_term: str          # 标准术语
    synonym: str                 # 同义词
    source: str                  # manual/ai_suggested
    confidence: float            # 置信度（AI 建议时）
    
    created_at: datetime
    created_by: str | None       # 创建者
    is_active: bool              # 是否启用
```

### 批量任务 (Batch_Task)

```python
class BatchTask(Base):
    __tablename__ = "batch_tasks"
    
    id: str                      # UUID
    user_id: str | None          # 用户 ID
    status: str                  # pending/running/completed/cancelled/failed
    
    # 任务内容
    total_items: int             # 总输入数量
    processed_items: int         # 已处理数量
    successful_items: int        # 成功数量
    failed_items: int            # 失败数量
    
    # 详细结果
    item_results: list[dict]     # 每项处理结果
    
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
```

### 通知 (Notification)

```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id: str                      # UUID
    user_id: str                 # 接收用户 ID
    notification_type: str       # new_proposal/timeout/urgent/system
    
    title: str                   # 通知标题
    content: str                 # 通知内容
    related_id: str | None       # 关联对象 ID
    
    is_read: bool                # 是否已读
    created_at: datetime
    read_at: datetime | None
```

### 节点关联 (Node_Relation)

```python
class NodeRelation(Base):
    __tablename__ = "node_relations"
    
    id: str                      # UUID
    source_node_id: str          # 源节点 ID
    target_node_id: str          # 目标节点 ID
    relation_type: str           # related/depends_on/extends
    
    created_at: datetime
    created_by_proposal_id: str | None  # 创建该关联的提案 ID
```


## 组件接口设计

### 输入处理器

```python
# services/input/input_processor.py
from dataclasses import dataclass
from enum import Enum

class InputType(Enum):
    URL = "url"
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "markdown"
    IMAGE = "image"
    TEXT = "text"

@dataclass
class ProcessedInput:
    success: bool
    input_type: InputType
    extracted_text: str
    metadata: dict              # 标题、作者、日期等
    error_message: str | None

class InputProcessor:
    def __init__(self, file_parser: FileParser, web_fetcher: WebFetcher, ai_client: SiliconFlowClient):
        self.file_parser = file_parser
        self.web_fetcher = web_fetcher
        self.ai_client = ai_client
    
    async def process(self, input_data: str | bytes, input_type: InputType) -> ProcessedInput:
        """处理单个输入，返回提取的文本内容"""
        pass
    
    async def process_url(self, url: str) -> ProcessedInput:
        """处理 URL 输入"""
        pass
    
    async def process_file(self, file_content: bytes, filename: str) -> ProcessedInput:
        """处理文件上传"""
        pass
    
    async def process_text(self, text: str) -> ProcessedInput:
        """处理纯文本输入"""
        pass
```

### 文件解析器

```python
# services/input/file_parser.py
@dataclass
class ParseResult:
    success: bool
    text: str
    metadata: dict
    error_message: str | None

class FileParser:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    async def parse_pdf(self, content: bytes) -> ParseResult:
        """解析 PDF 文件"""
        pass
    
    async def parse_word(self, content: bytes) -> ParseResult:
        """解析 Word 文档"""
        pass
    
    async def parse_markdown(self, content: bytes) -> ParseResult:
        """解析 Markdown 文件"""
        pass
    
    async def ocr_image(self, content: bytes) -> ParseResult:
        """OCR 识别图片文字"""
        pass
    
    def validate_file_size(self, content: bytes) -> bool:
        """验证文件大小"""
        return len(content) <= self.MAX_FILE_SIZE
```

### 概念提取器

```python
# services/concept/concept_extractor.py
@dataclass
class ExtractedConcept:
    name: str
    concept_type: str          # technology/tool/method/organization
    confidence: float          # 0-1
    context: str               # 概念出现的上下文
    related_concepts: list[str]  # 相关概念

@dataclass
class ExtractionResult:
    concepts: list[ExtractedConcept]
    relations: list[dict]      # 概念间关系
    ai_reasoning: str          # AI 推理过程

class ConceptExtractor:
    def __init__(self, ai_client: SiliconFlowClient):
        self.ai_client = ai_client
    
    async def extract(self, text: str) -> ExtractionResult:
        """从文本中提取概念"""
        pass
    
    async def analyze_relations(self, concepts: list[ExtractedConcept]) -> list[dict]:
        """分析概念间关系"""
        pass
```

### 概念匹配器

```python
# services/concept/concept_matcher.py
@dataclass
class MatchResult:
    concept: ExtractedConcept
    match_type: str            # exact/similar/new
    matched_node_id: str | None
    similarity_score: float
    suggested_action: str      # link/rename/split/add

class ConceptMatcher:
    def __init__(self, synonym_manager: SynonymManager, ai_client: SiliconFlowClient):
        self.synonym_manager = synonym_manager
        self.ai_client = ai_client
    
    async def match(self, concept: ExtractedConcept, pyramid_id: str) -> MatchResult:
        """匹配概念到金字塔节点"""
        pass
    
    async def find_similar_nodes(self, concept_name: str, pyramid_id: str) -> list[dict]:
        """查找相似节点"""
        pass
    
    async def calculate_similarity(self, concept_name: str, node_name: str) -> float:
        """计算概念与节点的相似度"""
        pass
```


### 提案生成器

```python
# services/proposal/proposal_generator.py
class ProposalGenerator:
    def __init__(self, ai_client: SiliconFlowClient):
        self.ai_client = ai_client
    
    async def generate_add_node_proposal(
        self,
        concept: ExtractedConcept,
        pyramid_id: str,
        suggested_parent_id: str,
        contribution_id: str | None = None
    ) -> ChangeProposal:
        """生成添加节点提案"""
        pass
    
    async def generate_rename_proposal(
        self,
        node_id: str,
        new_name: str,
        reason: str,
        contribution_id: str | None = None
    ) -> ChangeProposal:
        """生成重命名提案"""
        pass
    
    async def generate_split_proposal(
        self,
        node_id: str,
        split_suggestions: list[dict],
        contribution_id: str | None = None
    ) -> ChangeProposal:
        """生成拆分提案"""
        pass
    
    async def generate_merge_proposal(
        self,
        node_ids: list[str],
        merged_name: str,
        contribution_id: str | None = None
    ) -> ChangeProposal:
        """生成合并提案"""
        pass
    
    async def generate_relation_proposal(
        self,
        source_node_id: str,
        target_node_id: str,
        relation_type: str,
        contribution_id: str | None = None
    ) -> ChangeProposal:
        """生成关联提案"""
        pass
```

### 审批队列管理器

```python
# services/proposal/approval_queue.py
@dataclass
class QueuedProposal:
    proposal: ChangeProposal
    queue_position: int
    wait_time_hours: float

class ApprovalQueueManager:
    TIMEOUT_DAYS = 7
    
    async def enqueue(self, proposal: ChangeProposal) -> None:
        """将提案加入队列"""
        pass
    
    async def get_queue(
        self,
        status: str | None = None,
        proposal_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        size: int = 20
    ) -> list[QueuedProposal]:
        """获取队列列表"""
        pass
    
    async def get_proposal_detail(self, proposal_id: str) -> ChangeProposal:
        """获取提案详情"""
        pass
    
    async def check_timeouts(self) -> list[ChangeProposal]:
        """检查超时提案"""
        pass
    
    async def batch_approve(self, proposal_ids: list[str], reviewer: str) -> list[dict]:
        """批量审批"""
        pass
    
    async def batch_reject(self, proposal_ids: list[str], reviewer: str, reason: str) -> list[dict]:
        """批量拒绝"""
        pass
```

### 影响分析器

```python
# services/proposal/impact_analyzer.py
@dataclass
class ImpactReport:
    affected_nodes_count: int
    affected_contents_count: int
    affected_sources_count: int
    risk_level: str            # low/medium/high
    affected_nodes: list[dict]
    affected_contents: list[dict]
    affected_source_mappings: list[dict]
    reclassification_needed: list[str]  # 需要重新分类的内容 ID
    before_preview: dict       # 变更前预览
    after_preview: dict        # 变更后预览

class ImpactAnalyzer:
    async def analyze(self, proposal: ChangeProposal) -> ImpactReport:
        """分析提案影响"""
        pass
    
    async def calculate_risk_level(self, proposal: ChangeProposal) -> str:
        """计算风险等级"""
        pass
    
    async def generate_preview(self, proposal: ChangeProposal) -> dict:
        """生成变更预览"""
        pass
```

### 决策执行器

```python
# services/proposal/decision_executor.py
@dataclass
class ExecutionResult:
    success: bool
    proposal_id: str
    executed_changes: list[dict]
    error_message: str | None
    snapshot_id: str | None

class DecisionExecutor:
    def __init__(self, snapshot_manager: SnapshotManager):
        self.snapshot_manager = snapshot_manager
    
    async def approve(self, proposal_id: str, reviewer: str, comment: str | None = None) -> ExecutionResult:
        """批准并执行提案"""
        pass
    
    async def reject(self, proposal_id: str, reviewer: str, reason: str) -> None:
        """拒绝提案"""
        pass
    
    async def modify(self, proposal_id: str, reviewer: str, modifications: dict) -> ChangeProposal:
        """修改提案（创建新版本）"""
        pass
    
    async def dry_run(self, proposal_id: str) -> dict:
        """预览执行结果（不实际执行）"""
        pass
    
    async def execute_add_node(self, payload: dict) -> dict:
        """执行添加节点"""
        pass
    
    async def execute_rename_node(self, payload: dict) -> dict:
        """执行重命名节点"""
        pass
    
    async def execute_split_node(self, payload: dict) -> dict:
        """执行拆分节点"""
        pass
    
    async def execute_merge_nodes(self, payload: dict) -> dict:
        """执行合并节点"""
        pass
    
    async def execute_add_relation(self, payload: dict) -> dict:
        """执行添加关联"""
        pass
```


### 快照管理器

```python
# services/snapshot/snapshot_manager.py
class SnapshotManager:
    RETENTION_DAYS = 30
    
    async def create_snapshot(self, proposal: ChangeProposal) -> StateSnapshot:
        """创建变更前快照"""
        pass
    
    async def rollback(self, snapshot_id: str) -> ExecutionResult:
        """回滚到快照状态"""
        pass
    
    async def get_snapshot(self, snapshot_id: str) -> StateSnapshot:
        """获取快照详情"""
        pass
    
    async def preview_rollback(self, snapshot_id: str) -> dict:
        """预览回滚结果"""
        pass
    
    async def list_snapshots(self, proposal_id: str | None = None) -> list[StateSnapshot]:
        """列出快照"""
        pass
    
    async def cleanup_expired(self) -> int:
        """清理过期快照"""
        pass
    
    def validate_snapshot(self, snapshot: StateSnapshot) -> bool:
        """验证快照完整性"""
        pass
```

### 优先级计算器

```python
# services/proposal/priority_calculator.py
class PriorityCalculator:
    # 类型权重
    TYPE_WEIGHTS = {
        "merge_nodes": 50,      # 合并影响最大
        "split_node": 40,
        "add_node": 20,
        "rename_node": 10,
        "add_relation": 15
    }
    
    # 来源权重
    SOURCE_WEIGHTS = {
        "user_input": 30,       # 用户贡献优先
        "system_discovery": 20,
        "ai_suggestion": 10
    }
    
    def calculate(self, proposal: ChangeProposal, impact: ImpactReport) -> int:
        """计算优先级分数 (1-100)"""
        pass
    
    def calculate_type_score(self, proposal_type: str) -> int:
        """计算类型分数"""
        pass
    
    def calculate_impact_score(self, impact: ImpactReport) -> int:
        """计算影响分数"""
        pass
    
    def calculate_wait_time_score(self, created_at: datetime) -> int:
        """计算等待时间分数"""
        pass
```

### 贡献追踪器

```python
# services/contribution/contribution_tracker.py
@dataclass
class ContributionStats:
    total_contributions: int
    adopted_count: int
    rejected_count: int
    pending_count: int
    adoption_rate: float

class ContributionTracker:
    async def create_contribution(
        self,
        user_id: str | None,
        input_type: str,
        original_input: str,
        extracted_content: str
    ) -> Contribution:
        """创建贡献记录"""
        pass
    
    async def update_status(self, contribution_id: str, status: str, reason: str | None = None) -> None:
        """更新贡献状态"""
        pass
    
    async def link_proposal(self, contribution_id: str, proposal_id: str) -> None:
        """关联提案"""
        pass
    
    async def get_user_contributions(self, user_id: str, page: int = 1, size: int = 20) -> list[Contribution]:
        """获取用户贡献历史"""
        pass
    
    async def get_user_stats(self, user_id: str) -> ContributionStats:
        """获取用户贡献统计"""
        pass
```

### 同义词管理器

```python
# services/concept/synonym_manager.py
class SynonymManager:
    async def add_synonym(self, canonical_term: str, synonym: str, source: str = "manual") -> SynonymMapping:
        """添加同义词"""
        pass
    
    async def remove_synonym(self, mapping_id: str) -> None:
        """移除同义词"""
        pass
    
    async def get_synonyms(self, term: str) -> list[str]:
        """获取术语的所有同义词"""
        pass
    
    async def expand_search(self, term: str) -> list[str]:
        """扩展搜索词（包含同义词）"""
        pass
    
    async def bulk_import(self, mappings: list[dict]) -> int:
        """批量导入同义词"""
        pass
    
    async def suggest_synonyms(self, term: str) -> list[dict]:
        """AI 建议同义词"""
        pass
```

### 通知服务

```python
# services/notification/notification_service.py
class NotificationService:
    async def send_new_proposal_notification(self, proposal: ChangeProposal, recipients: list[str]) -> None:
        """发送新提案通知"""
        pass
    
    async def send_timeout_reminder(self, proposal: ChangeProposal, recipients: list[str]) -> None:
        """发送超时提醒"""
        pass
    
    async def send_urgent_notification(self, proposal: ChangeProposal, recipients: list[str]) -> None:
        """发送紧急通知"""
        pass
    
    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        """获取用户通知"""
        pass
    
    async def mark_as_read(self, notification_ids: list[str]) -> None:
        """标记为已读"""
        pass
    
    async def get_unread_count(self, user_id: str) -> int:
        """获取未读数量"""
        pass
```


## API 端点

```python
# 输入处理
POST /api/input/url                    # 提交 URL
POST /api/input/file                   # 上传文件
POST /api/input/text                   # 提交文本
POST /api/input/batch                  # 批量提交
GET  /api/input/batch/{task_id}        # 获取批量任务状态
DELETE /api/input/batch/{task_id}      # 取消批量任务

# 提案管理
GET  /api/proposals                    # 获取提案列表
GET  /api/proposals/{id}               # 获取提案详情
GET  /api/proposals/{id}/impact        # 获取影响分析
POST /api/proposals/{id}/dry-run       # 预览执行结果

# 审批操作
POST /api/approvals/{id}/approve       # 批准提案
POST /api/approvals/{id}/reject        # 拒绝提案
POST /api/approvals/{id}/modify        # 修改提案
POST /api/approvals/batch/approve      # 批量批准
POST /api/approvals/batch/reject       # 批量拒绝

# 快照与回滚
GET  /api/snapshots                    # 获取快照列表
GET  /api/snapshots/{id}               # 获取快照详情
POST /api/snapshots/{id}/rollback      # 执行回滚
GET  /api/snapshots/{id}/preview       # 预览回滚

# 贡献记录
GET  /api/contributions                # 获取贡献列表
GET  /api/contributions/{id}           # 获取贡献详情
GET  /api/contributions/stats          # 获取贡献统计

# 同义词管理
GET  /api/synonyms                     # 获取同义词列表
POST /api/synonyms                     # 添加同义词
DELETE /api/synonyms/{id}              # 删除同义词
POST /api/synonyms/bulk                # 批量导入

# 通知
GET  /api/notifications                # 获取通知列表
POST /api/notifications/read           # 标记已读
GET  /api/notifications/unread-count   # 获取未读数量

# 变更历史
GET  /api/history                      # 获取变更历史
GET  /api/history/{id}                 # 获取变更详情
GET  /api/history/export               # 导出历史报告
```

## Prompt 模板

### 概念提取 Prompt

```python
CONCEPT_EXTRACTION_PROMPT = """
你是一个 AI 领域知识专家。请从以下内容中提取关键概念。

内容：
{content}

请识别内容中的关键概念，并按以下格式返回 JSON：
{{
    "concepts": [
        {{
            "name": "概念名称",
            "type": "technology|tool|method|organization",
            "confidence": 0.0-1.0,
            "context": "概念出现的上下文片段"
        }}
    ],
    "relations": [
        {{
            "source": "概念A",
            "target": "概念B",
            "relation": "related|depends_on|extends"
        }}
    ],
    "reasoning": "提取过程的推理说明"
}}

注意：
1. 只提取与 AI/机器学习/大模型相关的概念
2. 概念类型说明：
   - technology: 技术、算法、架构（如 Transformer、RAG）
   - tool: 工具、框架、库（如 LangChain、PyTorch）
   - method: 方法、技术、实践（如 Few-shot Learning）
   - organization: 组织、公司、团队（如 OpenAI、Anthropic）
3. 置信度反映概念识别的确定性
"""
```

### 概念相似度计算 Prompt

```python
SIMILARITY_CALCULATION_PROMPT = """
请评估以下两个概念的相似度。

概念 A：{concept_a}
概念 B：{concept_b}

请返回 JSON 格式：
{{
    "similarity_score": 0.0-1.0,
    "is_synonym": true|false,
    "relationship": "same|similar|related|different",
    "reasoning": "相似度判断的理由"
}}

评估标准：
- 1.0: 完全相同的概念
- 0.8-0.99: 同义词或极其相似
- 0.5-0.79: 相关但有区别
- 0.2-0.49: 弱相关
- 0.0-0.19: 不相关
"""
```

### 变更理由生成 Prompt

```python
CHANGE_REASON_PROMPT = """
请为以下金字塔结构变更生成详细的理由说明。

变更类型：{change_type}
变更内容：{change_details}
触发来源：{source_content}

请返回 JSON 格式：
{{
    "reason": "变更的主要理由",
    "benefits": ["好处1", "好处2"],
    "risks": ["风险1", "风险2"],
    "recommendation": "建议采纳|建议谨慎|建议拒绝"
}}
"""
```


## 正确性属性

*正确性属性是系统应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 文件解析往返一致性
*For any* 包含文本内容的 PDF、Word 或 Markdown 文件，解析提取的文本应包含原始文件中的所有文字内容（忽略格式）。
**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: 输入处理贡献记录完整性
*For any* 成功处理的用户输入，系统中应存在对应的 Contribution 记录，且记录包含正确的输入类型和提取内容。
**Validates: Requirements 1.9**

### Property 3: 批量处理完整性
*For any* 包含 N 个输入项的批量任务，任务完成后 processed_items 应等于 N，且 successful_items + failed_items 应等于 N。
**Validates: Requirements 1.7, 17.2**

### Property 4: 概念提取结构完整性
*For any* AI 返回的概念列表，每个概念必须包含 name（非空字符串）、type（有效类型枚举）和 confidence（0-1 范围的浮点数）。
**Validates: Requirements 2.2**

### Property 5: 概念匹配决策一致性
*For any* 概念与节点的匹配结果，如果相似度为 1.0 则 match_type 应为 "exact"，如果相似度 > 0.8 则应生成重命名或拆分提案，如果相似度 < 0.5 则应生成添加节点提案。
**Validates: Requirements 3.2, 3.3, 3.4**

### Property 6: 提案内容完整性
*For any* 生成的变更提案，必须包含：唯一 ID、提案类型、payload（符合类型对应的结构）、AI 推理说明、置信度分数。
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7**

### Property 7: 提案 ID 唯一性
*For any* 两个不同的变更提案，它们的 ID 必须不同。
**Validates: Requirements 4.6, 5.1**

### Property 8: 审批队列排序正确性
*For any* 审批队列查询结果，返回的提案列表应按优先级降序排列，优先级相同时按创建时间升序排列。
**Validates: Requirements 5.3**

### Property 9: 影响分析完整性
*For any* 变更提案的影响分析报告，必须包含：受影响节点数量、受影响内容数量、受影响信息源数量、风险等级（low/medium/high）。
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**

### Property 10: 审批决策状态一致性
*For any* 被批准的提案，执行成功后状态应为 "executed"，执行失败后状态应保持 "approved" 且有错误记录；被拒绝的提案状态应为 "rejected" 且有拒绝原因。
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 11: Dry-run 不变性
*For any* 提案的 dry-run 执行，执行前后金字塔结构应完全相同，不应有任何节点、关联或内容分类发生变化。
**Validates: Requirements 7.6**

### Property 12: 快照回滚往返一致性
*For any* 已执行的变更，创建快照后执行变更再回滚，回滚后的金字塔结构应与快照中保存的结构完全一致。
**Validates: Requirements 8.1, 8.2**

### Property 13: 快照完整性校验
*For any* 状态快照，其 checksum 应与快照数据的实际校验和一致；如果不一致，回滚操作应被阻止并返回错误。
**Validates: Requirements 8.7**

### Property 14: 贡献统计正确性
*For any* 用户的贡献统计，adoption_rate 应等于 adopted_count / total_contributions，且 total_contributions 应等于 adopted_count + rejected_count + pending_count。
**Validates: Requirements 9.5**

### Property 15: 优先级分数范围
*For any* 计算的提案优先级分数，值必须在 1-100 范围内。
**Validates: Requirements 13.5**

### Property 16: 同义词搜索扩展
*For any* 概念匹配搜索，如果概念 A 有同义词 B，则搜索 A 时应同时搜索 B，搜索 B 时应同时搜索 A。
**Validates: Requirements 14.3**

### Property 17: 批量处理容错性
*For any* 批量任务中的单个输入处理失败，不应影响其他输入的处理，任务应继续执行直到所有输入都被处理。
**Validates: Requirements 17.3**

### Property 18: 文件大小限制
*For any* 上传的文件，如果大小超过 10MB，系统应拒绝处理并返回明确的错误信息。
**Validates: Requirements 16.6**


## 错误处理

### API 错误响应格式

```python
class ErrorResponse(BaseModel):
    code: str           # 错误码
    message: str        # 错误信息
    details: dict = {}  # 详细信息

# 新增错误码
ERROR_CODES = {
    # 输入处理错误
    "INPUT_PARSE_FAILED": "输入内容解析失败",
    "UNSUPPORTED_FILE_TYPE": "不支持的文件类型",
    "FILE_TOO_LARGE": "文件大小超过限制",
    "URL_FETCH_FAILED": "URL 内容获取失败",
    "OCR_FAILED": "OCR 识别失败",
    
    # 概念处理错误
    "CONCEPT_EXTRACTION_FAILED": "概念提取失败",
    "CONCEPT_MATCH_FAILED": "概念匹配失败",
    
    # 提案错误
    "PROPOSAL_NOT_FOUND": "提案不存在",
    "PROPOSAL_ALREADY_PROCESSED": "提案已被处理",
    "PROPOSAL_EXECUTION_FAILED": "提案执行失败",
    "INVALID_PROPOSAL_TYPE": "无效的提案类型",
    
    # 快照错误
    "SNAPSHOT_NOT_FOUND": "快照不存在",
    "SNAPSHOT_CORRUPTED": "快照数据损坏",
    "ROLLBACK_FAILED": "回滚操作失败",
    
    # 批量处理错误
    "BATCH_TASK_NOT_FOUND": "批量任务不存在",
    "BATCH_LIMIT_EXCEEDED": "批量任务数量超过限制",
    "BATCH_CANCELLED": "批量任务已取消",
    
    # AI 服务错误
    "AI_SERVICE_UNAVAILABLE": "AI 服务不可用",
    "AI_RATE_LIMITED": "AI 服务调用频率限制",
}
```

### 错误处理策略

| 错误类型 | 处理方式 | HTTP 状态码 |
|---------|---------|------------|
| 文件解析失败 | 返回详细错误信息 | 422 |
| 文件过大 | 拒绝处理 | 413 |
| 提案不存在 | 返回 404 | 404 |
| 提案已处理 | 返回冲突错误 | 409 |
| 快照损坏 | 阻止回滚，返回错误 | 500 |
| AI 服务不可用 | 重试后返回错误 | 503 |
| 批量任务超限 | 拒绝创建 | 400 |

## 测试策略

### 单元测试

- 文件解析器各格式解析逻辑
- 概念提取结果结构验证
- 概念匹配算法
- 优先级计算逻辑
- 快照创建和校验
- 同义词扩展逻辑

### 属性测试

使用 Hypothesis 库进行属性测试，每个属性测试运行至少 100 次迭代。

测试标签格式：`Feature: ai-radar-iteration-3, Property N: {property_text}`

```python
# 属性测试示例
from hypothesis import given, strategies as st

@given(st.binary(min_size=1, max_size=1000))
def test_markdown_parse_roundtrip(content):
    """Property 1: 文件解析往返一致性"""
    # 创建包含随机文本的 Markdown
    text = content.decode('utf-8', errors='ignore')
    md_content = f"# Title\n\n{text}"
    
    # 解析
    result = file_parser.parse_markdown(md_content.encode())
    
    # 验证文本内容被保留
    assert text in result.text or result.success == False

@given(st.lists(st.text(min_size=1), min_size=1, max_size=10))
def test_batch_processing_completeness(inputs):
    """Property 3: 批量处理完整性"""
    task = batch_processor.create_task(inputs)
    batch_processor.execute(task.id)
    
    result = batch_processor.get_status(task.id)
    assert result.processed_items == len(inputs)
    assert result.successful_items + result.failed_items == len(inputs)
```

### 集成测试

- 完整输入处理流程（输入→解析→概念提取→匹配→提案生成）
- 审批流程（提案→审批→执行→快照）
- 回滚流程（执行→回滚→验证）
- AI 服务调用（使用真实 API，限制调用次数）

### Mock 策略

- AI 服务使用 mock 响应进行单元测试
- 文件解析使用预生成的测试文件
- 集成测试使用真实 AI 服务（限制调用次数）

### 测试数据生成策略

```python
from hypothesis import strategies as st

# 概念生成策略
concept_strategy = st.fixed_dictionaries({
    'name': st.text(min_size=1, max_size=50),
    'type': st.sampled_from(['technology', 'tool', 'method', 'organization']),
    'confidence': st.floats(min_value=0.0, max_value=1.0),
    'context': st.text(max_size=200)
})

# 提案类型策略
proposal_type_strategy = st.sampled_from([
    'add_node', 'rename_node', 'split_node', 'merge_nodes', 'add_relation'
])

# 优先级分数策略
priority_strategy = st.integers(min_value=1, max_value=100)
```

