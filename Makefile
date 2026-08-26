# SevaSetu AI — Makefile
# Author: Rahul Jha | Made in India 🇮🇳
# Usage: make <target>

.PHONY: help install dev test lint build docker-up docker-down migrate seed clean

# ── Help ──────────────────────────────────────────────────────
help:
	@echo "SevaSetu AI — Available commands 🇮🇳"
	@echo "---------------------------------------"
	@echo "make install     Install all dependencies"
	@echo "make dev         Start dev servers (backend + frontend)"
	@echo "make test        Run all tests"
	@echo "make lint        Lint backend + frontend"
	@echo "make build       Build frontend production bundle"
	@echo "make docker-up   Start full stack with Docker Compose"
	@echo "make docker-down Stop Docker Compose"
	@echo "make migrate     Run Alembic database migrations"
	@echo "make seed        Seed database with sample data"
	@echo "make clean       Remove build artifacts and caches"

# ── Install ────────────────────────────────────────────────────
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed"

# ── Development ────────────────────────────────────────────────
dev-backend:
	@echo "🚀 Starting FastAPI backend on http://localhost:8000"
	cd backend && uvicorn app.main:app --reload --port 8000 --log-level info

dev-frontend:
	@echo "🚀 Starting React frontend on http://localhost:3000"
	cd frontend && npm start

dev:
	@echo "🚀 Starting SevaSetu AI development servers..."
	$(MAKE) -j2 dev-backend dev-frontend

# ── Database ────────────────────────────────────────────────────
db-create:
	@echo "🗄️ Creating MySQL database..."
	mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sevasetu_db CHARACTER SET utf8mb4;"
	mysql -u root -p -e "CREATE USER IF NOT EXISTS 'sevasetu'@'localhost' IDENTIFIED BY 'password';"
	mysql -u root -p -e "GRANT ALL PRIVILEGES ON sevasetu_db.* TO 'sevasetu'@'localhost';"

migrate:
	@echo "🔄 Running database migrations..."
	cd backend && alembic upgrade head

migrate-rollback:
	cd backend && alembic downgrade -1

seed:
	@echo "🌱 Seeding database with government schemes..."
	mysql -u sevasetu -p sevasetu_db < database/schema.sql

# ── Testing ─────────────────────────────────────────────────────
test:
	@echo "🧪 Running backend tests..."
	cd backend && pytest tests/ -v --asyncio-mode=auto --tb=short

test-coverage:
	cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --asyncio-mode=auto
	@echo "📊 Coverage report: backend/htmlcov/index.html"

test-auth:
	cd backend && pytest tests/test_auth.py -v --asyncio-mode=auto

test-queries:
	cd backend && pytest tests/test_queries.py -v --asyncio-mode=auto

test-schemes:
	cd backend && pytest tests/test_schemes.py -v --asyncio-mode=auto

# ── Linting ─────────────────────────────────────────────────────
lint-backend:
	@echo "🔍 Linting backend..."
	cd backend && python -m flake8 app/ --max-line-length=120 --ignore=E501,W503
	cd backend && python -m mypy app/ --ignore-missing-imports

lint-frontend:
	@echo "🔍 Linting frontend..."
	cd frontend && npm run lint

lint: lint-backend lint-frontend
	@echo "✅ All linting passed"

# ── Build ───────────────────────────────────────────────────────
build-frontend:
	@echo "🏗️ Building React frontend for production..."
	cd frontend && npm run build
	@echo "✅ Frontend built → frontend/build/"

build: build-frontend
	@echo "✅ Production build complete"

# ── Docker ──────────────────────────────────────────────────────
docker-up:
	@echo "🐳 Starting SevaSetu AI with Docker Compose..."
	cd docker && docker-compose up --build

docker-up-detached:
	cd docker && docker-compose up --build -d
	@echo "✅ SevaSetu AI running in background"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Swagger:  http://localhost:8000/docs"

docker-down:
	@echo "🛑 Stopping SevaSetu AI containers..."
	cd docker && docker-compose down

docker-logs:
	cd docker && docker-compose logs -f

docker-logs-backend:
	cd docker && docker-compose logs -f backend

docker-clean:
	cd docker && docker-compose down -v --remove-orphans

# ── PDF Reports ──────────────────────────────────────────────────
test-pdf:
	@echo "📄 Testing PDF generation..."
	cd backend && python -c "from app.api.reports import _generate_checklist_pdf; print('PDF service OK')"

# ── OCR ─────────────────────────────────────────────────────────
test-ocr:
	@echo "🔍 Testing Tesseract OCR..."
	tesseract --version
	@echo "✅ Tesseract is installed"

# ── AI / RAG ────────────────────────────────────────────────────
test-rag:
	@echo "🤖 Testing RAG engine initialization..."
	cd backend && python -c "import asyncio; from ai.rag.rag_engine import rag_engine; asyncio.run(rag_engine.initialize()); print('RAG engine OK')"

index-knowledge-base:
	@echo "📚 Indexing knowledge base into ChromaDB..."
	cd backend && python -c "import asyncio; from ai.rag.rag_engine import rag_engine; asyncio.run(rag_engine.initialize()); print(f'Indexed {rag_engine.collection.count()} documents')"

# ── Cleanup ──────────────────────────────────────────────────────
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf frontend/build frontend/node_modules/.cache
	rm -rf backend/__pycache__ backend/app/__pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

# ── Cloud Deployment ─────────────────────────────────────────────
deploy-gcp:
	@echo "☁️ Deploying to Google Cloud Run..."
	gcloud builds submit --tag gcr.io/$$GCP_PROJECT/sevasetu-backend ./backend
	gcloud run deploy sevasetu-backend --image gcr.io/$$GCP_PROJECT/sevasetu-backend --region asia-south1 --allow-unauthenticated

deploy-aws:
	@echo "☁️ Deploying to AWS Elastic Beanstalk..."
	cd docker && eb deploy production

# ── Info ─────────────────────────────────────────────────────────
info:
	@echo "SevaSetu AI v1.0.0"
	@echo "Author: Rahul Jha"
	@echo "Made in India 🇮🇳"
	@echo ""
	@echo "Tech Stack:"
	@echo "  Frontend : React 18, React Router 6, CSS Modules, Axios"
	@echo "  Backend  : Python 3.11, FastAPI, SQLAlchemy async, Alembic"
	@echo "  AI/RAG   : Gemini API, ChromaDB, Sentence-BERT"
	@echo "  OCR      : Tesseract 5 (EN+HI+MR), OpenCV, PyMuPDF"
	@echo "  Database : MySQL 8.0, Redis 7"
	@echo "  Deploy   : Docker Compose, Nginx, AWS/GCP"
