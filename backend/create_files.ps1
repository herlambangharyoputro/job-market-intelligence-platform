# Script untuk membuat semua file yang dibutuhkan
# Run: .\create_files.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Creating FastAPI Project Files" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Create app/__init__.py
Write-Host "Creating app/__init__.py..." -ForegroundColor Green
New-Item -Path app\__init__.py -ItemType File -Force | Out-Null

# Create app/main.py
Write-Host "Creating app/main.py..." -ForegroundColor Green
@"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API untuk analisis lowongan pekerjaan menggunakan NLP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Job Market Intelligence Platform API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "job-market-intelligence-platform-api",
        "database": "mysql"
    }

@app.get("/api/v1/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "database": "MySQL",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }
"@ | Out-File -FilePath app\main.py -Encoding UTF8

# Create app/config.py
Write-Host "Creating app/config.py..." -ForegroundColor Green
@"
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Job Market Intelligence Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    MAX_TEXT_LENGTH: int = 10000
    DEFAULT_LANGUAGE: str = "id"
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    ENABLE_SKILL_EXTRACTION: bool = True
    
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
"@ | Out-File -FilePath app\config.py -Encoding UTF8

# Create database files
Write-Host "Creating database files..." -ForegroundColor Green

# app/database/__init__.py
@"
from app.database.base import Base
from app.database.session import engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
"@ | Out-File -FilePath app\database\__init__.py -Encoding UTF8

# app/database/base.py
@"
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"@ | Out-File -FilePath app\database\base.py -Encoding UTF8

# app/database/session.py
@"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"@ | Out-File -FilePath app\database\session.py -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✓ All files created successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created files:" -ForegroundColor Yellow
Write-Host "  - app/__init__.py"
Write-Host "  - app/main.py"
Write-Host "  - app/config.py"
Write-Host "  - app/database/__init__.py"
Write-Host "  - app/database/base.py"
Write-Host "  - app/database/session.py"
Write-Host ""
Write-Host "Now you can run:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
