# SevaSetu AI 🇮🇳
## AI-Powered Public Service Assistant for Government Scheme Guidance

> **"Bridging Citizens to Government Services"**
> Developed by **Rahul Jha** | Made in India 🇮🇳

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://react.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🌟 Features

| Feature | Technology |
|---------|-----------|
| 🤖 AI Chat (RAG) | Gemini API + ChromaDB + Sentence-BERT |
| 🗳️ 10+ Government Services | Voter ID, PAN, Passport, Certificates |
| 🏛️ 100+ Government Schemes | Central + State, Eligibility Scoring |
| 📄 Document OCR | Tesseract (EN+HI+MR), Field Extraction |
| 🌐 Multilingual | English, Hindi, Marathi |
| 🎤 Voice Input/Output | Web Speech API |
| 🔐 Auth | JWT + bcrypt + RBAC |
| 📊 Admin Panel | Analytics, User & Scheme Management |
| 📥 PDF Reports | ReportLab — Professional PDFs |
| 🐳 Deployment | Docker Compose + Nginx |

---

## 🏗️ Project Structure

```
sevasetu-ai/
├── frontend/                    # React.js Frontend
│   ├── src/
│   │   ├── App.jsx              # Root app + auth context + routing
│   │   ├── App.css              # Global design system CSS
│   │   ├── pages/
│   │   │   ├── SplashScreen.jsx # 3D animated intro screen
│   │   │   ├── LoginPage.jsx    # JWT login
│   │   │   ├── RegisterPage.jsx # User registration
│   │   │   ├── Dashboard.jsx    # User dashboard with stats
│   │   │   ├── ChatPage.jsx     # AI chatbot interface ⭐
│   │   │   ├── SchemesPage.jsx  # Scheme browser + eligibility
│   │   │   ├── DocumentsPage.jsx# Document upload + OCR + checklist
│   │   │   ├── HistoryPage.jsx  # Query history
│   │   │   ├── ReportsPage.jsx  # PDF report generation
│   │   │   ├── AdminPage.jsx    # Admin panel
│   │   │   └── ProfilePage.jsx  # User profile settings
│   │   ├── components/
│   │   │   ├── MainLayout.jsx   # Sidebar + topnav layout
│   │   │   ├── LoadingSpinner.jsx
│   │   │   └── ...
│   │   └── services/
│   │       └── api.js           # Axios API client (all endpoints)
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point ⭐
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   ├── auth.py          # JWT + bcrypt + RBAC
│   │   │   ├── database.py      # Async SQLAlchemy + MySQL
│   │   │   └── logging_config.py
│   │   ├── api/
│   │   │   ├── auth.py          # /auth/* endpoints
│   │   │   ├── queries.py       # /queries/* (RAG pipeline) ⭐
│   │   │   ├── schemes.py       # /schemes/* CRUD + eligibility
│   │   │   ├── documents.py     # /documents/* upload + OCR
│   │   │   ├── reports.py       # /reports/* PDF generation
│   │   │   ├── admin.py         # /admin/* analytics
│   │   │   ├── users.py         # /users/* profile
│   │   │   └── __init__.py
│   │   └── models/
│   │       └── user.py          # All SQLAlchemy models
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai/                          # AI/ML Modules
│   ├── rag/
│   │   └── rag_engine.py        # RAG pipeline (ChromaDB + Gemini) ⭐
│   ├── ocr/
│   │   └── ocr_engine.py        # Tesseract OCR + field extraction ⭐
│   └── embeddings/
│       └── embedding_service.py
│
├── database/
│   └── schema.sql               # MySQL schema + seed data ⭐
│
├── docs/
│   └── PROJECT_DOCUMENTATION.md # Complete SRS, Literature Survey, Viva QA ⭐
│
├── docker/
│   ├── docker-compose.yml       # Full stack deployment ⭐
│   └── nginx/
│       └── nginx.conf
│
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Tesseract OCR (with Hindi+Marathi packs)
- Docker & Docker Compose (for containerized deployment)

### 1. Clone Repository
```bash
git clone https://github.com/rahul-jha/sevasetu-ai.git
cd sevasetu-ai
```

### 2. Configure Environment
```bash
# Backend .env
cp backend/.env.example backend/.env

# Edit backend/.env:
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=mysql+asyncmy://sevasetu:password@localhost:3306/sevasetu_db
GEMINI_API_KEY=your-gemini-api-key-here    # Set this only in your backend host environment; never commit the real key    # Get from aistudio.google.com
REDIS_URL=redis://localhost:6379

# Frontend .env
echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env
```

### 3. Database Setup
```bash
mysql -u root -p < database/schema.sql
```

### 4. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Tesseract OCR (Ubuntu/Debian)
sudo apt-get install -y tesseract-ocr tesseract-ocr-hin tesseract-ocr-mar

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

### 6. Access Application
| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:3000 |
| 🔌 Backend API | http://localhost:8000 |
| 📖 Swagger Docs | http://localhost:8000/docs |
| 📊 ReDoc | http://localhost:8000/redoc |

**Default Admin Login:**
- Email: `admin@sevasetu.ai`
- Password: `Admin@SevaSetu1`

---

## 🐳 Docker Deployment

```bash
# Full stack with Docker Compose
cd docker
cp .env.example .env              # Configure your API keys
docker-compose up --build         # Development
docker-compose up -d              # Production (detached)

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down
```

---

## ☁️ Cloud Deployment (AWS/GCP)

### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init sevasetu-ai --region ap-south-1 --platform docker

# Create environment
eb create production --instance_type t3.medium

# Deploy
eb deploy
```

### Google Cloud Run
```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/sevasetu-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/sevasetu-frontend ./frontend

# Deploy backend
gcloud run deploy sevasetu-backend \
  --image gcr.io/PROJECT_ID/sevasetu-backend \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=xxx

# Deploy frontend
gcloud run deploy sevasetu-frontend \
  --image gcr.io/PROJECT_ID/sevasetu-frontend \
  --region asia-south1 \
  --allow-unauthenticated
```

---

## 🔌 API Quick Reference

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","mobile":"9876543210","password":"Test@1234","state":"Maharashtra"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@example.com&password=Test@1234"

# Ask AI (RAG)
curl -X POST http://localhost:8000/api/v1/queries/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"How to apply for PAN card?","language":"en"}'

# Check scheme eligibility
curl -X POST http://localhost:8000/api/v1/schemes/eligibility \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"annual_income":200000,"age":35,"gender":"male","is_farmer":true}'

# Upload document for OCR
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@aadhaar.jpg" \
  -F "service_type=voter_id"
```

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v --asyncio-mode=auto

# With coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🤖 Getting Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API Key"
4. Copy key into `backend/.env` as `GEMINI_API_KEY=xxx`

**Free tier:** 15 requests/minute, 1 million tokens/month — sufficient for development and testing.

---

## 📊 Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React.js 18, React Router 6 | Single Page Application |
| Styling | CSS Modules, Custom Properties | Design system |
| API Client | Axios + interceptors | HTTP + auth |
| Backend | FastAPI + Uvicorn | REST API |
| Auth | JWT + bcrypt | Authentication + RBAC |
| Database | MySQL 8 + SQLAlchemy async | Relational data |
| Cache | Redis 7 | Sessions + rate limit |
| AI/LLM | Google Gemini 1.5 Flash | Language generation |
| Vector DB | ChromaDB | Semantic search |
| Embeddings | Sentence-BERT (MiniLM) | Query embedding |
| OCR | Tesseract 5 + OpenCV | Document processing |
| PDF | ReportLab | Report generation |
| Container | Docker + Docker Compose | Deployment |
| Web Server | Nginx | Reverse proxy + SSL |

---

## 👨‍💻 Author

**Rahul Jha**
- Final Year AIML Student
- Project: SevaSetu AI — Government Services Assistant
- Made with ❤️ in India 🇮🇳
- Contact: rahul@sevasetu.ai

---

## 📜 License

MIT License — Free to use for educational purposes.

Copyright (c) 2026 Rahul Jha

---

## 🙏 Acknowledgements

- Google Gemini team for the powerful LLM API
- ChromaDB team for the vector database
- Hugging Face for Sentence-Transformers
- FastAPI team for the excellent Python web framework
- Government of India for the open scheme data

---

*Jai Hind! 🇮🇳 — SevaSetu AI: Bridging 1.4 Billion Citizens to Government Services*


## Render deployment

This project is configured for Render with `render.yaml`. Deploy the repository as a Blueprint. It creates a FastAPI Docker Web Service and a React Static Site.

Set these backend secrets in Render: `GEMINI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `SMTP_USER`, and `SMTP_PASSWORD`. The backend also generates a production `SECRET_KEY`.

The frontend uses `REACT_APP_API_URL` and must point to the Render FastAPI service root URL (do not append `/api/v1`).

For Forgot Password, configure Gmail SMTP with a Gmail App Password so the backend can send reset links.


For the complete Render deployment process, see `RENDER_DEPLOYMENT.md`.
