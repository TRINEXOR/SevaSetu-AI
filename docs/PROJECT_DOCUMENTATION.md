# SevaSetu AI — Complete Project Documentation
### AI-Powered Public Service Assistant for Government Scheme Guidance and Document Assistance
**Author:** Rahul Jha | **Made in India 🇮🇳** | Final Year Major Project (AIML)

---

## 📋 TABLE OF CONTENTS

1. Project Abstract
2. Problem Statement
3. Objectives
4. Literature Survey
5. Software Requirements Specification (SRS)
6. System Architecture
7. API Endpoints Reference
8. Testing Plan
9. Future Scope
10. Viva Questions & Answers

---

# 1. 📝 PROJECT ABSTRACT

**SevaSetu AI** (सेवासेतु AI — Bridge to Services) is a production-grade, AI-powered web application designed to bridge the information gap between Indian citizens and the vast ecosystem of government services and welfare schemes. Leveraging Retrieval-Augmented Generation (RAG) with Google Gemini LLM, the system provides accurate, contextual, multilingual guidance on 100+ central and state government schemes, document procedures (Voter ID, PAN Card, Passport, Birth Certificate, Income/Caste/Domicile Certificates), and eligibility checking.

The platform incorporates OCR-based document verification using Tesseract, enabling citizens to upload identity documents for automatic field extraction and checklist generation. A JWT-secured REST API backend (Python FastAPI) communicates with a React.js frontend featuring a ChatGPT-style conversational interface, voice input (Web Speech API), multilingual support (English, Hindi, Marathi), and PDF report generation.

The system addresses the challenge that millions of Indians, especially in rural/semi-urban areas, face in navigating bureaucratic processes due to language barriers, digital illiteracy, and lack of accessible guidance. SevaSetu AI democratizes this knowledge through a conversational, vernacular-language AI assistant deployable on cloud infrastructure with Docker containerization.

**Keywords:** RAG, Gemini API, ChromaDB, FastAPI, React.js, OCR, JWT, Government Schemes, Multilingual NLP, Document Verification, India

---

# 2. ❓ PROBLEM STATEMENT

India has over 1,000 central and state government welfare schemes covering agriculture, health, education, housing, and more — yet a large proportion of the eligible population remains unaware or unable to access these benefits due to:

1. **Language Barrier:** Most scheme documentation is in English; rural populations speak Hindi, regional languages
2. **Information Fragmentation:** Scheme details spread across dozens of government portals with inconsistent updates
3. **Document Ignorance:** Citizens don't know which documents are needed for which service, leading to repeated office visits
4. **Digital Divide:** Complex government portals with poor UX deter first-time internet users
5. **No Personalized Guidance:** Static FAQ pages can't answer "Am I eligible for this scheme?" dynamically
6. **Corruption Risk:** Information asymmetry forces citizens to rely on middlemen (dalals) who charge fees

**Scope of the Problem:**
- 813 million internet users in India, but government portal engagement remains low (Source: TRAI 2024)
- Only 42% of PM Kisan beneficiaries self-applied; rest used paid agents (Ministry of Agriculture data)
- 67% of Ayushman Bharat eligible families are unaware of their entitlement (PMJAY survey 2023)

**SevaSetu AI's Solution:** A conversational AI assistant that answers citizen questions in their preferred language, checks eligibility dynamically, generates document checklists, and provides step-by-step application guidance — all in one accessible interface.

---

# 3. 🎯 OBJECTIVES

### Primary Objectives
1. Build an AI chatbot using RAG + Gemini API that provides accurate, cited answers about government services
2. Implement multilingual support (English, Hindi, Marathi) for inclusive access
3. Create an OCR-based document verification system using Tesseract
4. Develop a scheme eligibility prediction engine using rule-based + ML scoring
5. Provide personalized document checklists for 10+ government services
6. Ensure secure, scalable deployment using Docker + JWT authentication

### Secondary Objectives
7. Design an admin panel for scheme management and usage analytics
8. Implement PDF report generation for offline reference
9. Add voice input/output using Web Speech API
10. Create a responsive UI accessible on all devices (mobile-first)
11. Document all APIs using Swagger/OpenAPI
12. Achieve >85% AI response accuracy on government service queries

### Educational Objectives
13. Demonstrate practical application of RAG architecture in a real-world system
14. Apply AIML knowledge (embeddings, vector search, LLM integration)
15. Practice full-stack development with production-grade code quality

---

# 4. 📚 LITERATURE SURVEY

### 4.1 Retrieval-Augmented Generation (RAG)
**Lewis et al. (2020)** — "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Facebook AI) introduced RAG as a framework combining parametric (LLM) and non-parametric (document retrieval) memory. RAG reduces hallucination by grounding LLM responses in retrieved factual context — critical for government information systems where accuracy is paramount.

**Application in SevaSetu AI:** We index a curated knowledge base of government scheme documents into ChromaDB. At query time, the top-k most semantically similar passages are retrieved and injected into the Gemini prompt as context, ensuring factual, up-to-date answers.

### 4.2 Large Language Models for Government Services
**Chen et al. (2023)** — GovAssist paper showed that fine-tuned LLMs on government FAQ datasets achieved 91% citizen satisfaction vs 67% for traditional chatbots. Key finding: RAG outperforms fine-tuning for frequently-changing government information since re-indexing is cheaper than re-training.

**UMANG (Unified Mobile Application for New-age Governance)** — India's existing government app with 22,000+ services. Lacks conversational AI, natural language understanding, and scheme eligibility checking. SevaSetu AI positions itself as the AI layer on top of such service ecosystems.

### 4.3 OCR for Document Verification
**Tesseract OCR (Google, 2006-present)** — Industry-standard open-source OCR engine. v5.0 introduced LSTM neural networks achieving 98%+ accuracy on printed text. SevaSetu AI uses Tesseract with Hindi (hin) and Marathi (mar) language packs alongside English (eng) for trilingual document processing.

**Preprocessing pipeline (OpenCV):** CLAHE contrast enhancement, adaptive thresholding, and bilateral denoising significantly improve OCR accuracy on poor-quality scanned documents — a common scenario with government photocopies.

### 4.4 Vector Databases for Semantic Search
**ChromaDB (2023)** — Lightweight, open-source embedding database optimized for AI applications. Compared to FAISS (Facebook), ChromaDB offers persistent storage, metadata filtering, and a Python-native API — ideal for our scheme knowledge base.

**Sentence-BERT (Reimers & Gurevych, 2019)** — all-MiniLM-L6-v2 model provides 384-dimensional sentence embeddings with excellent semantic similarity performance. 14x faster than BERT with comparable accuracy for retrieval tasks.

### 4.5 Multilingual NLP for Indian Languages
**IndicBERT (AI4Bharat, 2022)** — Multilingual BERT trained on 12 Indian languages. While we use Sentence-BERT for embeddings, IndicBERT's research confirms strong NLP performance for Hindi and Marathi, validating our multilingual approach.

**Challenges identified:** Hindi-English code-mixing (Hinglish) is common in citizen queries. Our system handles this through language detection (langdetect) + English-dominant embedding model, with Gemini's inherent multilingual capability handling mixed-language responses.

### 4.6 Government Chatbots — Existing Systems
| System | Country | Technology | Limitations |
|--------|---------|------------|-------------|
| iGOT Karmayogi | India | Rule-based | Training only, no citizen-facing |
| Ask DISCo | Delhi Police | NLP chatbot | Limited domain, English only |
| UMANG Chatbot | India | Intent classification | No RAG, limited scheme coverage |
| GovChatbot UK | UK | GPT-4 | English only, UK-specific |
| **SevaSetu AI** | **India** | **RAG + Gemini** | **Our contribution** |

### 4.7 Research Gap Addressed
Existing systems either (a) use simple rule-based responses without LLM, (b) cover single domains, (c) lack multilingual support, or (d) don't have document OCR integration. **SevaSetu AI integrates all these capabilities in a single production-ready system** — this is the novel contribution of this project.

---

# 5. 📋 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## 5.1 Introduction

### 5.1.1 Purpose
This SRS defines the functional and non-functional requirements for SevaSetu AI v1.0, an AI-powered government services assistant for Indian citizens.

### 5.1.2 Scope
The system provides:
- Conversational AI guidance on government schemes and document procedures
- Multilingual interface (English, Hindi, Marathi)
- Document OCR extraction and checklist generation
- Scheme eligibility checking
- User authentication with role-based access
- Admin panel for system management

### 5.1.3 Definitions
- **RAG:** Retrieval-Augmented Generation — AI technique combining document retrieval with LLM generation
- **OCR:** Optical Character Recognition — extracting text from images/PDFs
- **JWT:** JSON Web Token — stateless authentication mechanism
- **ChromaDB:** Vector database for storing document embeddings
- **RBAC:** Role-Based Access Control

## 5.2 Overall Description

### 5.2.1 Product Perspective
SevaSetu AI is a standalone web application with RESTful API backend, AI processing layer, and React frontend. It integrates with:
- Google Gemini API (LLM)
- ChromaDB (vector store)
- MySQL (relational data)
- Tesseract OCR (document processing)

### 5.2.2 User Classes
| User Class | Description | Access Level |
|------------|-------------|--------------|
| Citizen (Guest) | Unregistered, limited access | Browse schemes |
| Citizen (User) | Registered, full access | Chat, upload docs, history |
| Admin | System administrator | Full + admin panel |

### 5.2.3 Operating Environment
- **Frontend:** Any modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Mobile:** iOS 13+, Android 8+
- **Backend:** Python 3.11+, Ubuntu 20.04+
- **Database:** MySQL 8.0+
- **Deployment:** Docker 24+, docker-compose 2.0+

## 5.3 Functional Requirements

### FR-01: User Registration and Authentication
- System shall allow citizens to register with name, email, mobile, state, language
- System shall validate Indian mobile numbers (10-digit, starts with 6-9)
- System shall hash passwords using bcrypt (min 8 chars, 1 uppercase, 1 digit)
- System shall issue JWT access tokens (24h expiry) and refresh tokens (30d)
- System shall support role-based access: User, Admin

### FR-02: AI Chat Interface
- System shall process natural language queries about government services
- System shall respond within 5 seconds for 95th percentile queries
- System shall use RAG pipeline: embed query → search ChromaDB → generate with Gemini
- System shall display source citations with AI responses
- System shall save all queries and responses to database
- System shall support voice input via Web Speech API
- System shall support queries in English, Hindi, and Marathi

### FR-03: Government Scheme Database
- System shall store 100+ government schemes with full details
- System shall support filtering by category, state, income, age, gender
- System shall provide scheme eligibility scoring (0-100%)
- Admin shall be able to add/edit/delete schemes
- System shall support full-text search across scheme names and descriptions

### FR-04: Document Management
- System shall accept PDF, JPG, PNG, TIFF uploads (max 10MB)
- System shall run Tesseract OCR on uploaded documents (English + Hindi + Marathi)
- System shall extract structured fields (name, DOB, Aadhaar, address, etc.)
- System shall detect document type automatically
- System shall generate document checklists for 10+ government services
- System shall calculate document verification score (0-100%)

### FR-05: Report Generation
- System shall generate PDF reports for individual query answers
- System shall generate PDF for document checklists
- System shall allow export of complete query history as PDF
- PDFs shall include SevaSetu AI branding and disclaimer

### FR-06: Admin Panel
- Admin shall view system-wide analytics (users, queries, schemes, documents)
- Admin shall manage user accounts (activate/deactivate, change roles)
- Admin shall manage government schemes (CRUD)
- Admin shall view daily query trends
- Admin shall view query category distribution

### FR-07: Multi-language Support
- System shall detect query language automatically
- System shall respond in the same language as the query
- System shall allow user language preference setting
- Interface labels shall be available in English, Hindi, Marathi

### FR-08: Notifications
- System shall send welcome email on registration
- System shall send email with PDF report when requested
- Emails shall be sent asynchronously (non-blocking)

## 5.4 Non-Functional Requirements

### NFR-01: Performance
- API response time ≤ 2s for non-AI endpoints (99th percentile)
- AI query response time ≤ 8s (95th percentile)
- System shall handle 100 concurrent users
- OCR processing ≤ 30s per document

### NFR-02: Security
- All API endpoints (except login/register) require JWT authentication
- Passwords stored as bcrypt hashes (cost factor 12)
- CORS configured to allow only approved origins
- File uploads validated for type and size before processing
- SQL injection prevented via SQLAlchemy ORM parameterized queries
- Aadhaar numbers masked (XXXX XXXX XXXX) in storage and display
- HTTPS enforced in production via Nginx + SSL

### NFR-03: Reliability
- System uptime: 99.5% (allows ~43 minutes downtime/month)
- Database: daily automated backups with 30-day retention
- Graceful error handling — no stack traces exposed to users
- Background task failures logged and retried

### NFR-04: Scalability
- Stateless JWT authentication enables horizontal scaling
- Docker-based deployment supports container orchestration (Kubernetes)
- ChromaDB and MySQL support clustering for high availability

### NFR-05: Usability
- Mobile-responsive UI (min 320px to 4K screens)
- WCAG 2.1 Level AA accessibility compliance
- Page load time ≤ 3s on 4G connection
- Voice input available on supported browsers

### NFR-06: Maintainability
- All code documented with docstrings
- Swagger/OpenAPI documentation auto-generated
- Docker Compose for reproducible environments
- Alembic migrations for database schema changes
- Structured logging with log levels

---

# 6. 🔗 API ENDPOINTS REFERENCE

## Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/register | ❌ | Register new user |
| POST | /api/v1/auth/login | ❌ | Login, get JWT |
| POST | /api/v1/auth/refresh | ❌ | Refresh access token |
| POST | /api/v1/auth/logout | ✅ | Logout |
| GET | /api/v1/auth/me | ✅ | Current user profile |
| POST | /api/v1/auth/change-password | ✅ | Change password |

## AI Queries
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/queries/ask | ✅ | Ask AI assistant (RAG) |
| GET | /api/v1/queries/history | ✅ | User query history |
| GET | /api/v1/queries/suggestions | ✅ | Query suggestions |
| GET | /api/v1/queries/{id} | ✅ | Single query detail |
| DELETE | /api/v1/queries/{id} | ✅ | Delete query |
| POST | /api/v1/queries/feedback | ✅ | Rate AI response |

## Government Schemes
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/v1/schemes/ | ✅ | List schemes (filtered) |
| GET | /api/v1/schemes/categories | ✅ | Scheme categories |
| GET | /api/v1/schemes/{id} | ✅ | Scheme details |
| POST | /api/v1/schemes/eligibility | ✅ | Check eligibility |
| POST | /api/v1/schemes/ | 🔐 Admin | Create scheme |
| PUT | /api/v1/schemes/{id} | 🔐 Admin | Update scheme |
| DELETE | /api/v1/schemes/{id} | 🔐 Admin | Delete scheme |

## Documents
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/documents/upload | ✅ | Upload for OCR |
| GET | /api/v1/documents/ | ✅ | List documents |
| GET | /api/v1/documents/{id} | ✅ | Document + OCR results |
| GET | /api/v1/documents/checklist/{svc} | ✅ | Document checklist |
| DELETE | /api/v1/documents/{id} | ✅ | Delete document |

## Reports
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/v1/reports/query/{id} | ✅ | Query answer PDF |
| GET | /api/v1/reports/history | ✅ | History export PDF |
| GET | /api/v1/reports/checklist/{svc} | ✅ | Checklist PDF |

## Admin
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/v1/admin/dashboard | 🔐 Admin | Analytics overview |
| GET | /api/v1/admin/users | 🔐 Admin | All users |
| PUT | /api/v1/admin/users/{id} | 🔐 Admin | Update user |
| GET | /api/v1/admin/queries | 🔐 Admin | All queries |
| GET | /api/v1/admin/stats/daily | 🔐 Admin | Daily usage stats |
| GET | /api/v1/admin/stats/schemes | 🔐 Admin | Scheme statistics |

---

# 7. 🧪 TESTING PLAN

## 7.1 Testing Strategy
SevaSetu AI uses a multi-layer testing approach:

| Test Type | Tool | Coverage Target |
|-----------|------|-----------------|
| Unit Tests | pytest + pytest-asyncio | 80%+ |
| Integration Tests | httpx TestClient | All API endpoints |
| AI Quality Tests | Custom evaluator | >85% accuracy |
| OCR Tests | Test document suite | 90%+ field extraction |
| Load Tests | Locust | 100 concurrent users |
| Security Tests | OWASP ZAP | No critical vulns |
| UI Tests | Playwright | Critical user flows |

## 7.2 Unit Test Cases

### Auth Module
| Test ID | Test Case | Expected Result |
|---------|-----------|----------------|
| UT-01 | Register with valid data | 201 Created, JWT returned |
| UT-02 | Register with duplicate email | 409 Conflict |
| UT-03 | Register with invalid mobile | 422 Validation Error |
| UT-04 | Login with correct credentials | 200 OK, tokens returned |
| UT-05 | Login with wrong password | 401 Unauthorized |
| UT-06 | Access protected route without JWT | 401 Unauthorized |
| UT-07 | Access admin route as user | 403 Forbidden |
| UT-08 | Refresh with valid refresh token | 200 OK, new access token |
| UT-09 | Refresh with expired token | 401 Unauthorized |

### AI Query Module
| Test ID | Test Case | Expected Result |
|---------|-----------|----------------|
| UT-10 | Ask about Voter ID | Contains "voters.eci.gov.in", documents list |
| UT-11 | Ask about PAN Card | Contains "Form 49A", fee, portal URL |
| UT-12 | Ask about Passport | Contains "PSK", steps, fee |
| UT-13 | Ask about PM Kisan | Contains "₹6,000", eligibility criteria |
| UT-14 | Ask in Hindi | Response in Hindi (Devanagari) |
| UT-15 | Empty question | 400 Bad Request |
| UT-16 | Question > 1000 chars | 400 Bad Request |
| UT-17 | Query saved to history | DB record created |

### Scheme Eligibility
| Test ID | Test Case | Expected Result |
|---------|-----------|----------------|
| UT-18 | Farmer income ₹80K checks PM Kisan | Score ≥ 0.7 (eligible) |
| UT-19 | Income taxpayer checks PM Kisan | Score < 0.5 |
| UT-20 | Female user checks BBBP | Score ≥ 0.7 |
| UT-21 | Male user checks PMMVY | Score < 0.3 |
| UT-22 | All schemes eligibility check | Returns sorted list |

### Document OCR
| Test ID | Test Case | Expected Result |
|---------|-----------|----------------|
| UT-23 | Upload Aadhaar image | Extracts name, DOB, masked number |
| UT-24 | Upload PAN card | Extracts PAN number (ABCDE1234F format) |
| UT-25 | Upload corrupt file | 400 Bad Request |
| UT-26 | Upload file > 10MB | 413 Request Too Large |
| UT-27 | Upload unsupported format | 400 Bad Request |
| UT-28 | Get checklist for voter_id | Returns required docs list |

## 7.3 Integration Tests

```python
# Example integration test (pytest)
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_query_flow():
    """Test: Register → Login → Ask → Get History → Export PDF"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register
        reg = await client.post("/api/v1/auth/register", json={
            "name": "Test User", "email": "test@sevasetu.ai",
            "mobile": "9876543210", "password": "Test@1234",
            "state": "Maharashtra", "language": "en"
        })
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Ask AI
        ask = await client.post("/api/v1/queries/ask",
            json={"question": "How to apply for PAN Card?"},
            headers=headers
        )
        assert ask.status_code == 200
        data = ask.json()
        assert data["success"] == True
        assert "PAN" in data["answer"] or "pan" in data["answer"].lower()
        assert data["confidence"] > 0
        query_id = data["query_id"]

        # Verify in history
        hist = await client.get("/api/v1/queries/history", headers=headers)
        assert hist.status_code == 200
        assert hist.json()["total"] >= 1

        # Export PDF
        pdf = await client.get(f"/api/v1/reports/query/{query_id}", headers=headers)
        assert pdf.status_code == 200
        assert pdf.headers["content-type"] == "application/pdf"
```

## 7.4 AI Quality Evaluation

**Test Dataset:** 50 manually crafted question-answer pairs across 10 categories.

**Evaluation Metrics:**
- **Accuracy:** Does response contain the correct key facts?
- **Completeness:** Are required documents, fees, and steps mentioned?
- **Citation:** Does response reference correct portal/helpline?
- **Language Fidelity:** Is Hindi response in proper Devanagari?

**Target:** ≥ 85% accuracy (42/50 questions answered correctly)

## 7.5 Load Testing Results (Target)

Using Locust with 100 concurrent users, 10-minute test:
| Metric | Target | 
|--------|--------|
| Average response time | < 2000ms |
| 95th percentile | < 5000ms |
| Requests per second | > 50 |
| Error rate | < 1% |
| AI endpoint (ask) | < 8000ms avg |

---

# 8. 🔮 FUTURE SCOPE

## Phase 2 (Next 6 months)
1. **Fine-tuned Model:** Fine-tune an IndicBERT/Llama model on Indian government scheme corpus for better Hindi/regional language handling
2. **Voice-First Interface:** Integrate ElevenLabs or Google TTS for natural-sounding Hindi/Marathi voice responses
3. **WhatsApp Integration:** Deploy SevaSetu AI as a WhatsApp Business API chatbot (most accessible for rural users)
4. **Aadhaar eKYC Integration:** Verify user identity via Aadhaar OTP for personalized scheme enrollment
5. **SMS Fallback:** USSD/SMS interface for users without smartphones

## Phase 3 (6-12 months)
6. **Live Application Tracking:** API integration with DigiLocker, UMANG, and state government portals for real-time application status
7. **Scheme Application Assistant:** Guide users through the actual online application forms step-by-step
8. **Offline Mode (PWA):** Service worker caching for offline scheme browsing
9. **GIS Integration:** District-level scheme availability mapping with interactive maps
10. **Grievance Redressal:** Integration with CPGRAMS (Centralized Public Grievance Redress and Monitoring System)

## Phase 4 (12-24 months)
11. **Federated Learning:** Privacy-preserving model improvement using anonymized citizen interaction data across districts
12. **Vernacular Expansion:** Add 10+ more Indian languages (Tamil, Telugu, Bengali, Kannada, Gujarati, Punjabi)
13. **Government Portal:** API partnerships with NIC, DigiLocker for official scheme data feed
14. **AI Paralegal:** Legal aid guidance for RTI (Right to Information) applications and grievance filing
15. **Predictive Analytics:** Forecast scheme budget absorption and suggest proactive outreach to eligible non-beneficiaries

## Research Extensions
- Comparison of RAG vs fine-tuning for Indian government domain
- Multilingual embedding evaluation for Indic languages
- Document forgery detection using CNN on OCR images
- Privacy-preserving eligibility checking using zero-knowledge proofs

---

# 9. ❓ VIVA QUESTIONS & ANSWERS

### Category A: AI/ML Concepts

**Q1: What is RAG (Retrieval-Augmented Generation) and why did you use it?**
A: RAG is an AI framework that combines document retrieval with LLM generation. Instead of relying solely on the LLM's training data (which may be outdated or hallucinated), RAG first retrieves relevant documents from a knowledge base, then uses them as context for the LLM's response. We used RAG for SevaSetu AI because: (1) Government scheme details change frequently — RAG allows us to update the knowledge base without retraining; (2) It reduces hallucination by anchoring responses in factual retrieved content; (3) It provides citations so users can verify information; (4) It's cost-effective compared to fine-tuning.

**Q2: What is ChromaDB and why not use a traditional database for vectors?**
A: ChromaDB is a purpose-built vector database optimized for storing and querying high-dimensional embedding vectors. Traditional databases like MySQL store scalar/string data and support exact-match queries. For semantic search, we need to find the "closest" documents to a query embedding using cosine similarity or L2 distance — operations that require specialized indexing (HNSW algorithms) that traditional DBs don't support efficiently. ChromaDB provides persistent storage, metadata filtering, and Python-native APIs with millisecond-latency similarity search over millions of vectors.

**Q3: What embedding model did you use and why?**
A: We use `all-MiniLM-L6-v2` from the Sentence-Transformers library. Reasons: (1) It produces 384-dimensional embeddings — compact yet semantically rich; (2) Inference is 14x faster than full BERT with comparable retrieval accuracy; (3) It works well for English and has partial Hindi support; (4) Runs locally without API calls, reducing latency and cost. For production, we'd upgrade to `intfloat/multilingual-e5-large` for better Indic language support.

**Q4: How does your scheme eligibility prediction work?**
A: It's a rule-based scoring engine. When a user provides their profile (income, age, gender, state, occupation), we evaluate each scheme against their profile using eligibility criteria stored in the database as JSON. Each matching criterion adds to a score (0-1). For example: if a scheme has max_income=₹3L and user earns ₹2L, score += 0.2. If user is female and scheme is female-only, score += 0.1. Final score determines Eligible (≥70%), Partial (40-70%), or Not Eligible (<40%). Future enhancement: train a binary classifier on historical enrollment data.

**Q5: How does your OCR pipeline handle poor quality documents?**
A: Our preprocessing pipeline has 5 steps: (1) Grayscale conversion to eliminate color noise; (2) CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance local contrast in uneven lighting; (3) Bilateral denoising to remove scanner artifacts while preserving edges; (4) Adaptive Gaussian thresholding for binarization (better than global threshold for uneven backgrounds); (5) Unsharp masking for text edge enhancement. After preprocessing, Tesseract uses LSTM (--oem 3) with PSM 6 (uniform block) for best results on mixed-language documents.

### Category B: Backend/API

**Q6: Why FastAPI over Django or Flask?**
A: FastAPI advantages: (1) Native async/await support for high concurrency without threading; (2) Auto-generated Swagger/OpenAPI documentation; (3) Pydantic models for automatic request validation; (4) 3-10x faster than Flask for IO-bound tasks; (5) Type hints integration for better IDE support and fewer runtime errors. Django would add unnecessary overhead (ORM session management, templating) for a pure API backend.

**Q7: Explain your JWT authentication flow.**
A: (1) User POSTs credentials to `/auth/login`; (2) Server verifies password against bcrypt hash; (3) Server creates access token (24h) with `{sub: user_id, role: user_role, exp: timestamp}` signed with SECRET_KEY using HS256; (4) Server also creates refresh token (30 days); (5) Client stores tokens (localStorage/httpOnly cookie); (6) For every subsequent request, client sends `Authorization: Bearer <token>`; (7) FastAPI dependency `get_current_user` decodes and validates the token; (8) When access token expires, client uses refresh token to get a new one without re-login.

**Q8: Why use async SQLAlchemy instead of synchronous?**
A: FastAPI is built on Starlette which uses Python's asyncio event loop. Using synchronous SQLAlchemy would block the event loop during DB queries, preventing the server from handling other requests concurrently — effectively making it single-threaded. `asyncmy` (async MySQL driver) + SQLAlchemy async session allows the server to process other requests while waiting for DB I/O, achieving higher throughput with fewer resources.

**Q9: How is document upload handled securely?**
A: Multi-layer security: (1) File extension whitelist (pdf, jpg, png, tiff only); (2) Python `magic` library checks actual MIME type (not just extension) — prevents `.php` renamed as `.jpg`; (3) File size limit (10MB) enforced before writing to disk; (4) UUID-based stored filenames prevent path traversal attacks; (5) Files stored outside web root so direct HTTP access is impossible; (6) Virus scanning can be added via ClamAV integration.

### Category C: Frontend

**Q10: How does voice input work in SevaSetu AI?**
A: We use the Web Speech API's `SpeechRecognition` interface, supported in Chrome and Edge. When the user clicks the microphone button: (1) We create a `SpeechRecognition` instance; (2) Set `lang` to the user's preferred language (e.g., `hi-IN` for Hindi); (3) `onresult` callback receives the transcript when speech ends; (4) The transcript populates the text input; (5) User can edit before sending. For TTS (Text-to-Speech), we use `SpeechSynthesisUtterance` to read AI responses aloud. Fallback: if API unsupported (Safari/Firefox), we gracefully disable the mic button.

**Q11: How did you implement the ChatGPT-like streaming effect?**
A: We simulate streaming by: (1) Showing a "typing" animation (three bouncing dots) while the API call is in progress; (2) When the response arrives, we split it into words and add them progressively with a small timeout using `setInterval`; (3) The message container auto-scrolls to the latest content. True streaming would use Server-Sent Events (SSE) with FastAPI's `StreamingResponse`, sending tokens as Gemini generates them — a production enhancement.

### Category D: Architecture & Deployment

**Q12: Explain your Docker deployment architecture.**
A: We use Docker Compose with 5 services: (1) **MySQL** — persistent relational data, health-checked; (2) **Redis** — session caching and rate limiting; (3) **ChromaDB** — vector store with persistent volume; (4) **FastAPI backend** — depends on MySQL/Redis/ChromaDB being healthy before starting; (5) **React frontend** — served by Nginx, depends on backend being healthy. Networks: all services on a private `sevasetu-net` bridge network. Only frontend (port 80/443) and backend (port 8000) are exposed to host. Production adds an Nginx reverse proxy with SSL termination.

**Q13: How would you scale SevaSetu AI for 1 million users?**
A: Scaling strategy: (1) **Horizontal backend scaling** — JWT is stateless, deploy 3-5 FastAPI instances behind a load balancer; (2) **Database** — MySQL read replicas for query history, connection pooling with PgBouncer; (3) **Redis cluster** — distribute session cache and rate limiting; (4) **ChromaDB** — deploy on dedicated server with SSD for vector operations; (5) **CDN** — CloudFront for static assets (React build); (6) **AI caching** — cache Gemini responses for identical/similar queries using Redis; (7) **Kubernetes** — container orchestration with auto-scaling based on CPU/memory; (8) **Queue** — Celery + RabbitMQ for OCR processing to prevent API timeouts.

**Q14: What security vulnerabilities did you consider?**
A: Addressed: (1) SQL Injection — SQLAlchemy ORM parameterized queries; (2) XSS — React auto-escapes content, CSP headers via Nginx; (3) CSRF — CORS whitelist + SameSite cookies; (4) Path Traversal — UUID filenames, no user-controlled file paths; (5) Brute Force — rate limiting (60 req/min general, 5 req/min login); (6) Sensitive Data Exposure — Aadhaar numbers masked, HTTPS enforced; (7) Broken Auth — short JWT expiry (24h), refresh token rotation; (8) Injection in AI prompts — user input sanitized before embedding in prompts, system prompt clearly separates instructions from user content.

**Q15: What is the difference between ChromaDB and FAISS?**
A: FAISS (Facebook AI Similarity Search) is a library for efficient vector similarity search — it's extremely fast and memory-efficient, but stores data in-memory (must serialize to disk manually), has no built-in metadata storage, and requires more code to use. ChromaDB is a full vector database built on top of FAISS (and DuckDB/SQLite) that adds: persistent storage, collection management, metadata filtering, document deduplication, and a Python/REST API. For SevaSetu AI's scale (hundreds of scheme documents), ChromaDB's developer experience advantage outweighs FAISS's raw performance. For billions of vectors, FAISS would be preferable.

---

*Document Version: 1.0 | Last Updated: June 2026*
*SevaSetu AI — Bridging Citizens to Government Services*
*Author: Rahul Jha | Made in India 🇮🇳 | Jai Hind!*
