from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Optional

class AIMetricBase(BaseModel):
    module: Optional[str] = None
    model: str
    provider: str
    latency: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    status: str
    error_message: Optional[str] = None

class AIMetricOut(AIMetricBase):
    id: UUID4
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PaginatedAIMetrics(BaseModel):
    total: int
    items: List[AIMetricOut]
    page: int
    page_size: int

class ModelStat(BaseModel):
    model: str
    count: int
    avg_latency: float
    total_tokens: int
    success_rate: float

class AIStatsOut(BaseModel):
    total_requests: int
    success_rate: float
    total_tokens: int
    avg_latency: float
    models: List[ModelStat]

class CleanMetricsIn(BaseModel):
    days: int = 30
