from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_sources: int
    active_sources: int
    discovered_domains: int
    whitelisted_domains: int
    total_contents: int
    validation_pass_rate: float
