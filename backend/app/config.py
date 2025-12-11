from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Job Market Intelligence Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database - Main URL
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Database - Optional separate components (tidak wajib)
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # NLP Settings
    MAX_TEXT_LENGTH: int = 10000
    DEFAULT_LANGUAGE: str = "id"
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    ENABLE_SKILL_EXTRACTION: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()