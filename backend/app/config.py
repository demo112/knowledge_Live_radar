from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Radar"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_radar.db"
    
    # Environment
    ENVIRONMENT: str = "development"

    # AI Service (SiliconFlow)
    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
