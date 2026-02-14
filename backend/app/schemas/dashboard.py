from pydantic import BaseModel
from typing import List

class DashboardStats(BaseModel):
    total_sources: int
    active_sources: int
    discovered_domains: int
    whitelisted_domains: int
    total_contents: int
    validation_pass_rate: float

class DailyTrend(BaseModel):
    date: str
    total_validations: int
    pass_rate: float

class DashboardTrend(BaseModel):
    trends: List[DailyTrend]
