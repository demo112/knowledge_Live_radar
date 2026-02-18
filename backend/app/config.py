from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Radar"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_radar.db"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"

    # AI Service (SiliconFlow)
    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"

    # Vector DB
    VECTOR_DB_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Evolution: Drift Detection
    DRIFT_OLD_DAYS: int = 30       # Content older than N days = "historical"
    DRIFT_NEW_DAYS: int = 7        # Content newer than N days = "recent"
    DRIFT_SAMPLE_SIZE: int = 5     # Number of samples per side

    # Evolution: Strategy Adapter
    STRATEGY_FRESHNESS_THRESHOLD: float = 0.5   # Ratio above which we speed up
    STRATEGY_FAILURE_THRESHOLD: float = 0.4     # Failure rate above which we back off
    STRATEGY_SPEEDUP_FACTOR: float = 0.8
    STRATEGY_SLOWDOWN_FACTOR: float = 1.5
    STRATEGY_BACKOFF_FACTOR: float = 2.0

    # Evolution: Hotspot
    HOTSPOT_TRENDING_COUNT: int = 10
    HOTSPOT_TRENDING_GROWTH: float = 20.0
    HOTSPOT_CLUSTER_THRESHOLD: int = 3

    # Firecrawl
    FIRECRAWL_API_URL: str = "http://localhost:3002"
    FIRECRAWL_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
