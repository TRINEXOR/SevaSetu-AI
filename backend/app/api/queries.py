"""
SevaSetu AI — AI Query API Router
Author: Rahul Jha | Made in India 🇮🇳

Endpoints:
  POST /api/v1/queries/ask         - Ask AI assistant (RAG pipeline)
  GET  /api/v1/queries/history     - Get user query history
  GET  /api/v1/queries/{id}        - Get single query detail
  DELETE /api/v1/queries/{id}      - Delete a query
  POST /api/v1/queries/feedback    - Submit feedback on AI response
  GET  /api/v1/queries/suggestions - Get query suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.query import QueryHistory, QueryFeedback
from ai.rag.rag_engine import rag_engine

logger = logging.getLogger(__name__)
router = APIRouter()


# ── SCHEMAS ──────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    language: Optional[str] = "en"   # en | hi | mr
    category: Optional[str] = None   # voter_id | pan | passport | scheme | etc.

class FeedbackRequest(BaseModel):
    query_id: int
    rating: int                       # 1-5
    comment: Optional[str] = None
    is_helpful: bool = True


# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/ask", summary="Ask the AI Assistant")
async def ask_ai(
    request: AskRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main AI query endpoint using RAG pipeline.

    Flow:
    1. Validate and preprocess user question
    2. Build user context from profile + history
    3. Run RAG engine (embed → search → generate)
    4. Save query + response to history
    5. Return answer with sources and confidence
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long (max 1000 characters)")

    # Build user context for personalization
    user_context = {
        "state": current_user.state,
        "language": current_user.language,
        "user_id": current_user.id,
    }

    # Get last 3 queries for context
    recent_result = await db.execute(
        select(QueryHistory)
        .where(QueryHistory.user_id == current_user.id)
        .order_by(desc(QueryHistory.created_at))
        .limit(3)
    )
    recent_queries = recent_result.scalars().all()
    if recent_queries:
        user_context["recent_queries"] = " | ".join([q.question for q in recent_queries])

    try:
        # Run RAG pipeline
        logger.info(f"🤖 RAG query from user {current_user.id}: {question[:80]}...")
        rag_result = await rag_engine.query(
            user_query=question,
            user_context=user_context,
            language=request.language or current_user.language or "en",
        )

        # Save to query history
        query_record = QueryHistory(
            user_id=current_user.id,
            question=question,
            ai_response=rag_result["answer"],
            category=request.category or _auto_detect_category(question),
            language=rag_result.get("language", "en"),
            confidence=rag_result.get("confidence", 0.0),
            sources=",".join(rag_result.get("sources", [])),
            created_at=datetime.now(timezone.utc),
        )
        db.add(query_record)
        await db.commit()
        await db.refresh(query_record)

        logger.info(f"✅ Query answered | ID: {query_record.id} | Confidence: {rag_result.get('confidence')}")

        return {
            "success": True,
            "query_id": query_record.id,
            "question": question,
            "answer": rag_result["answer"],
            "sources": rag_result.get("sources", []),
            "confidence": rag_result.get("confidence", 0.0),
            "language": rag_result.get("language", "en"),
            "category": query_record.category,
            "timestamp": str(query_record.created_at),
        }

    except Exception as e:
        logger.error(f"❌ Query processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable. Please try again in a moment."
        )


@router.get("/history", summary="Get query history")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated query history for the current user."""
    offset = (page - 1) * limit

    query = select(QueryHistory).where(QueryHistory.user_id == current_user.id)

    if category:
        query = query.where(QueryHistory.category == category)
    if search:
        query = query.where(QueryHistory.question.ilike(f"%{search}%"))

    # Total count
    count_query = select(func.count()).select_from(
        select(QueryHistory).where(QueryHistory.user_id == current_user.id).subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginated results
    query = query.order_by(desc(QueryHistory.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    queries = result.scalars().all()

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "data": [
            {
                "id": q.id,
                "question": q.question,
                "answer": q.ai_response,
                "category": q.category,
                "language": q.language,
                "confidence": q.confidence,
                "created_at": str(q.created_at),
            }
            for q in queries
        ],
    }


@router.get("/suggestions", summary="Get query suggestions")
async def get_suggestions(
    category: Optional[str] = None,
    language: str = "en",
    current_user: User = Depends(get_current_active_user),
):
    """Return context-aware query suggestions based on category and language."""
    suggestions_map = {
        "en": {
            "voter_id": [
                "How to correct name in Voter ID?",
                "How to apply for new Voter ID online?",
                "How to download Voter ID card (eEPIC)?",
                "What documents needed for Voter ID?",
            ],
            "pan": [
                "How to apply for PAN card online?",
                "What documents needed for PAN card?",
                "How to link PAN with Aadhaar?",
                "How to correct date of birth in PAN card?",
            ],
            "passport": [
                "What is the process for fresh passport?",
                "How to apply for Tatkal passport?",
                "What documents needed at Passport Seva Kendra?",
                "How to renew expired passport?",
            ],
            "schemes": [
                "Am I eligible for PM Kisan Yojana?",
                "How to apply for Ayushman Bharat card?",
                "What is PM Jan Dhan Yojana benefit?",
                "PM Awas Yojana eligibility criteria?",
            ],
            "default": [
                "How to apply for Voter ID card?",
                "What documents needed for passport?",
                "How to get income certificate?",
                "PM Kisan Yojana eligibility and benefits?",
                "How to apply for birth certificate?",
                "Ayushman Bharat card kaise banaye?",
            ],
        },
        "hi": {
            "default": [
                "वोटर आईडी कार्ड कैसे बनाएं?",
                "पैन कार्ड के लिए आवेदन कैसे करें?",
                "आयुष्मान भारत कार्ड कैसे बनाएं?",
                "पीएम किसान योजना के लिए पात्रता क्या है?",
                "जन्म प्रमाण पत्र कैसे बनाएं?",
            ],
        },
        "mr": {
            "default": [
                "मतदार ओळखपत्र कसे बनवायचे?",
                "पॅन कार्ड अर्ज कसा करायचा?",
                "उत्पन्न प्रमाणपत्र कसे मिळवायचे?",
                "जन्म दाखला कसा काढायचा?",
            ],
        },
    }

    lang_sug = suggestions_map.get(language, suggestions_map["en"])
    result = lang_sug.get(category or "default", lang_sug.get("default", []))
    return {"success": True, "suggestions": result}


@router.get("/{query_id}", summary="Get single query")
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a specific query by ID (must belong to current user)."""
    result = await db.execute(
        select(QueryHistory).where(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id,
        )
    )
    query = result.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    return {
        "id": query.id,
        "question": query.question,
        "answer": query.ai_response,
        "category": query.category,
        "language": query.language,
        "confidence": query.confidence,
        "sources": query.sources.split(",") if query.sources else [],
        "created_at": str(query.created_at),
    }


@router.delete("/{query_id}", summary="Delete a query")
async def delete_query(
    query_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a query from history (soft delete)."""
    result = await db.execute(
        select(QueryHistory).where(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id,
        )
    )
    query = result.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    await db.delete(query)
    await db.commit()
    return {"success": True, "message": "Query deleted"}


@router.post("/feedback", summary="Submit feedback on AI response")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit user feedback to improve AI quality."""
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Verify query belongs to user
    result = await db.execute(
        select(QueryHistory).where(
            QueryHistory.id == request.query_id,
            QueryHistory.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Query not found")

    feedback = QueryFeedback(
        query_id=request.query_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment,
        is_helpful=request.is_helpful,
    )
    db.add(feedback)
    await db.commit()

    logger.info(f"📊 Feedback received: Query {request.query_id} | Rating: {request.rating}/5")
    return {"success": True, "message": "Thank you for your feedback! 🙏"}


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _auto_detect_category(question: str) -> str:
    """Auto-detect query category from question text."""
    q = question.lower()
    if any(w in q for w in ["voter", "epic", "electoral", "vote"]):
        return "voter_id"
    elif any(w in q for w in ["pan card", "pan", "permanent account"]):
        return "pan_card"
    elif any(w in q for w in ["passport", "tatkal", "psk", "visa"]):
        return "passport"
    elif any(w in q for w in ["birth", "janam"]):
        return "birth_certificate"
    elif any(w in q for w in ["income", "aay", "salary certificate"]):
        return "income_certificate"
    elif any(w in q for w in ["caste", "jati", "sc", "st", "obc"]):
        return "caste_certificate"
    elif any(w in q for w in ["domicile", "residence", "niwas"]):
        return "domicile_certificate"
    elif any(w in q for w in ["kisan", "farmer", "agriculture", "krishi"]):
        return "agriculture_scheme"
    elif any(w in q for w in ["ayushman", "health", "hospital", "insurance"]):
        return "health_scheme"
    elif any(w in q for w in ["awas", "house", "housing", "ghar"]):
        return "housing_scheme"
    elif any(w in q for w in ["scholarship", "education", "vidya", "study"]):
        return "education_scheme"
    elif any(w in q for w in ["aadhaar", "aadhar", "uid"]):
        return "aadhaar"
    return "general"
