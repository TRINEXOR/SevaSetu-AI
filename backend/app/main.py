"""
SevaSetu AI - Main FastAPI Application
Author: Rahul Jha | Made in India 🇮🇳
Description: AI-Powered Public Service Assistant for Government Scheme Guidance
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, schemes, documents, queries, admin, reports
from app.core.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info("🚀 SevaSetu AI Backend Starting...")
    logger.info("📦 Creating database tables if not exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database ready")
    logger.info(f"🌐 Running on: {settings.API_BASE_URL}")
    logger.info("🇮🇳 SevaSetu AI - Made in India by Rahul Jha")
    yield
    # Shutdown
    logger.info("👋 SevaSetu AI Backend Shutting Down...")
    await engine.dispose()


# FastAPI app instance
app = FastAPI(
    title="SevaSetu AI API",
    description="""
## SevaSetu AI — Government Services Assistant API 🇮🇳

**Author:** Rahul Jha | **Made in India**

### Features
- 🤖 AI-powered government scheme guidance using RAG + Gemini
- 🗳️ Voter ID, PAN Card, Passport, Birth Certificate assistance
- 📋 Income, Caste, Domicile certificate guidance
- 🔍 Document OCR extraction with Tesseract
- 📊 Scheme eligibility prediction
- 🔐 JWT Authentication with Role-Based Access Control
- 🌐 Multi-language: English, Hindi, Marathi

### Authentication
Use `/auth/login` to get a JWT Bearer token, then include it in the `Authorization: Bearer <token>` header.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── MIDDLEWARE ──────────────────────────────────────────────────────────────

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    response.headers["X-Powered-By"] = "SevaSetu AI - Made in India 🇮🇳"
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 {request.method} {request.url.path} | IP: {request.client.host}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} → {response.status_code}")
    return response


# ── GLOBAL EXCEPTION HANDLER ────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error. Please try again.",
            "path": str(request.url.path),
        },
    )


# ── ROUTERS ─────────────────────────────────────────────────────────────────

app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["🔐 Authentication"])
app.include_router(users.router,     prefix="/api/v1/users",     tags=["👤 Users"])
app.include_router(schemes.router,   prefix="/api/v1/schemes",   tags=["🏛️ Schemes"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["📄 Documents"])
app.include_router(queries.router,   prefix="/api/v1/queries",   tags=["💬 AI Queries"])
app.include_router(admin.router,     prefix="/api/v1/admin",     tags=["⚙️ Admin"])
app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["📊 Reports"])


# ── HEALTH CHECK ────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "SevaSetu AI API"}


# ── SERVE REACT FRONTEND (SINGLE RENDER URL) ────────────────────────────────
# Render builds the React app before starting FastAPI. Serving the production
# build from the same process keeps the website and /api/v1 endpoints on one URL.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"
if FRONTEND_BUILD_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD_DIR), html=True), name="frontend")
