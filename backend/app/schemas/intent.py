from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class IntentType(str, Enum):
    LEARN = "learn"       # 学习新领域 (生成知识图谱)
    RESEARCH = "research" # 深入研究 (查找深度内容)
    TRACK = "track"       # 追踪动态 (订阅更新)
    CREATE = "create"     # 手动创建 (指定结构)
    GENERAL = "general"   # 通用/其他

class ActionType(str, Enum):
    CREATE_NODE = "create_node"
    CREATE_CLUSTER = "create_cluster"
    SEARCH_CONTENT = "search_content"
    GENERATE_REPORT = "generate_report"
    SUBSCRIBE_TOPIC = "subscribe_topic"

class Action(BaseModel):
    type: ActionType
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    
    model_config = ConfigDict(from_attributes=True)

class IntentParseResult(BaseModel):
    original_text: str
    intent_type: IntentType
    primary_topic: str
    sub_topics: List[str] = []
    goal: Optional[str] = None
    parameters: Dict[str, Any] = {}
    confidence: float = 1.0
    
    model_config = ConfigDict(from_attributes=True)

class IntentCreateRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=500)
    source: str = "user_input" # user_input, voice, etc.

class IntentResponse(BaseModel):
    id: str # Temporary ID or DB ID
    parsed_intent: IntentParseResult
    suggested_actions: List[Action] = []
    
    model_config = ConfigDict(from_attributes=True)
