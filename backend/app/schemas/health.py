from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

# Re-define enums or import if possible. 
# Importing from models can be tricky due to circular imports if models import schemas (rare)
# But models usually don't import schemas.
# Ideally we define Enums in a shared location or just use str.
# For simplicity, I'll use str or duplicate the enum if it's simple.

class HealthReportType(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    TRIGGERED = "triggered"

class HotspotStatus(str, Enum):
    EMERGING = "emerging"
    TRENDING = "trending"
    MATURE = "mature"
    COOLING = "cooling"
    ARCHIVED = "archived"

class HealthReportSchema(BaseModel):
    id: UUID
    report_type: HealthReportType
    overall_score: float
    pyramid_scores: Dict[str, float]
    source_health_score: float
    content_coverage_score: float
    hotspot_distribution: Dict[str, int]
    approval_backlog: Dict[str, Any]
    crawl_stats: Dict[str, Any]
    issues: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HotspotSchema(BaseModel):
    id: UUID
    topic_name: str
    status: HotspotStatus
    mention_count: int
    recent_7d_count: int
    previous_7d_count: int
    growth_rate: float
    display_priority: int
    first_seen_at: datetime
    last_mentioned_at: datetime

    model_config = ConfigDict(from_attributes=True)
