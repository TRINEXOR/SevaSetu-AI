"""
SevaSetu AI — Application Configuration
Author: Rahul Jha | Made in India 🇮🇳
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "SevaSetu AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "sevasetu-secret-key-change-in-production-rahul-jha"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Database (MySQL) ──────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://localhost/sevasetu_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour

    # ── AI / Gemini ───────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""                    # Set in .env
    OPENAI_API_KEY: str = ""                    # Fallback
    AI_MODEL: str = "gemini-2.0-flash"
    AI_MAX_TOKENS: int = 2048

    # ── ChromaDB (Vector DB) ──────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "/tmp/chroma_db"
    CHROMA_COLLECTION: str = "sevasetu_schemes"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # sentence-transformers model

    # ── FAISS (Alternative) ───────────────────────────────────────────────────
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    USE_FAISS: bool = False                     # Set True to use FAISS

    # ── OCR ───────────────────────────────────────────────────────────────────
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    TESSERACT_LANG: str = "eng+hin+mar"         # English + Hindi + Marathi
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "tiff"]

    # ── Email (SMTP) ──────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@sevasetu.ai"
    FROM_NAME: str = "SevaSetu AI 🇮🇳"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",    # React dev server
        "http://localhost:5173",    # Vite dev server
        "https://sevasetu.ai",      # Production
        "https://www.sevasetu.ai",
        "https://sevasetu-ai-web.onrender.com",
    ]

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AI_RATE_LIMIT_PER_MINUTE: int = 20

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/sevasetu.log"

    # ── PDF Reports ───────────────────────────────────────────────────────────
    REPORT_DIR: str = "./reports"
    REPORT_LOGO: str = "./assets/logo.png"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
