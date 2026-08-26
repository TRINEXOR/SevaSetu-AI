"""
SevaSetu AI — Admin Panel API Router
Author: Rahul Jha | Made in India 🇮🇳

All endpoints require Admin role (JWT with role=admin).

Endpoints:
  GET  /api/v1/admin/dashboard      - Analytics overview
  GET  /api/v1/admin/users          - List all users
  PUT  /api/v1/admin/users/{id}     - Update user (activate/deactivate/role)
  GET  /api/v1/admin/queries        - All query history (system-wide)
  GET  /api/v1/admin/stats/daily    - Daily usage stats
  GET  /api/v1/admin/stats/schemes  - Scheme query statistics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import logging

from app.core.database import get_db
from app.core.auth import get_admin_user
from app.models.user import (
    User, UserRole, QueryHistory, Document,
    Scheme, UserScheme, QueryFeedback, DocumentStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── SCHEMAS ──────────────────────────────────────────────────────────────────

class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    state: Optional[str] = None


# ── DASHBOARD ANALYTICS ───────────────────────────────────────────────────────

@router.get("/dashboard", summary="Admin dashboard analytics")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """
    Comprehensive analytics for admin dashboard:
    - User counts and growth
    - Query volume and trends
    - Top categories and schemes
    - Document processing stats
    - AI confidence averages
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    # ── User stats ────────────────────────────────────────────────────────────
    total_users_r = await db.execute(select(func.count(User.id)))
    total_users = total_users_r.scalar() or 0

    active_users_r = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_r.scalar() or 0

    new_users_week_r = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_start)
    )
    new_users_week = new_users_week_r.scalar() or 0

    # ── Query stats ───────────────────────────────────────────────────────────
    total_queries_r = await db.execute(select(func.count(QueryHistory.id)))
    total_queries = total_queries_r.scalar() or 0

    queries_today_r = await db.execute(
        select(func.count(QueryHistory.id)).where(QueryHistory.created_at >= today_start)
    )
    queries_today = queries_today_r.scalar() or 0

    queries_week_r = await db.execute(
        select(func.count(QueryHistory.id)).where(QueryHistory.created_at >= week_start)
    )
    queries_week = queries_week_r.scalar() or 0

    avg_confidence_r = await db.execute(
        select(func.avg(QueryHistory.confidence)).where(QueryHistory.confidence > 0)
    )
    avg_confidence = avg_confidence_r.scalar() or 0.0

    # ── Top categories ────────────────────────────────────────────────────────
    top_cats_r = await db.execute(
        select(QueryHistory.category, func.count(QueryHistory.id).label("cnt"))
        .where(QueryHistory.category.isnot(None))
        .group_by(QueryHistory.category)
        .order_by(desc("cnt"))
        .limit(6)
    )
    top_categories = [
        {"category": row.category, "count": row.cnt}
        for row in top_cats_r.all()
    ]

    # ── Document stats ────────────────────────────────────────────────────────
    total_docs_r = await db.execute(select(func.count(Document.id)))
    total_docs = total_docs_r.scalar() or 0

    completed_docs_r = await db.execute(
        select(func.count(Document.id)).where(Document.ocr_status == DocumentStatus.COMPLETED)
    )
    completed_docs = completed_docs_r.scalar() or 0

    # ── Scheme stats ──────────────────────────────────────────────────────────
    total_schemes_r = await db.execute(
        select(func.count(Scheme.id)).where(Scheme.is_active == True)
    )
    total_schemes = total_schemes_r.scalar() or 0

    # ── Feedback stats ────────────────────────────────────────────────────────
    avg_rating_r = await db.execute(
        select(func.avg(QueryFeedback.rating)).where(QueryFeedback.rating.isnot(None))
    )
    avg_rating = avg_rating_r.scalar() or 0.0

    # ── Language distribution ─────────────────────────────────────────────────
    lang_dist_r = await db.execute(
        select(QueryHistory.language, func.count(QueryHistory.id).label("cnt"))
        .group_by(QueryHistory.language)
    )
    language_distribution = [
        {"language": row.language or "en", "count": row.cnt}
        for row in lang_dist_r.all()
    ]

    # ── State distribution ────────────────────────────────────────────────────
    state_dist_r = await db.execute(
        select(User.state, func.count(User.id).label("cnt"))
        .where(User.state.isnot(None))
        .group_by(User.state)
        .order_by(desc("cnt"))
        .limit(8)
    )
    state_distribution = [
        {"state": row.state, "count": row.cnt}
        for row in state_dist_r.all()
    ]

    return {
        "success": True,
        "generated_at": str(now),
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "new_this_week": new_users_week,
        },
        "queries": {
            "total": total_queries,
            "today": queries_today,
            "this_week": queries_week,
            "avg_confidence": round(float(avg_confidence), 3),
        },
        "documents": {
            "total_uploaded": total_docs,
            "ocr_completed": completed_docs,
            "ocr_success_rate": round(completed_docs / total_docs, 3) if total_docs else 0,
        },
        "schemes": {
            "total_active": total_schemes,
        },
        "ai_quality": {
            "average_rating": round(float(avg_rating), 2),
            "avg_confidence": round(float(avg_confidence), 3),
        },
        "top_categories": top_categories,
        "language_distribution": language_distribution,
        "state_distribution": state_distribution,
    }


# ── USER MANAGEMENT ───────────────────────────────────────────────────────────

@router.get("/users", summary="List all users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin: Get paginated list of all registered users."""
    offset = (page - 1) * limit
    query = select(User)

    if search:
        query = query.where(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.mobile.ilike(f"%{search}%")
        )
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if state:
        query = query.where(User.state == state)

    total_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_r.scalar() or 0

    result = await db.execute(
        query.order_by(desc(User.created_at)).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    return {
        "success": True,
        "total": total,
        "page": page,
        "data": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "mobile": u.mobile,
                "state": u.state,
                "role": u.role.value,
                "language": u.language,
                "is_active": u.is_active,
                "created_at": str(u.created_at),
            }
            for u in users
        ],
    }


@router.put("/users/{user_id}", summary="Update user account")
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin: Activate/deactivate user or change their role."""
    from sqlalchemy import select as sa_select
    result = await db.execute(sa_select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    if request.is_active is not None:
        user.is_active = request.is_active
    if request.role is not None:
        user.role = request.role
    if request.state is not None:
        user.state = request.state

    await db.commit()
    action = "activated" if request.is_active else "updated"
    logger.info(f"👤 Admin {admin.email} {action} user {user.email}")
    return {"success": True, "message": f"User {action} successfully"}


# ── SYSTEM QUERY HISTORY ──────────────────────────────────────────────────────

@router.get("/queries", summary="All queries (system-wide)")
async def get_all_queries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin: View all queries made across all users."""
    offset = (page - 1) * limit
    query = select(QueryHistory)

    if category:
        query = query.where(QueryHistory.category == category)
    if language:
        query = query.where(QueryHistory.language == language)

    total_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_r.scalar() or 0

    result = await db.execute(
        query.order_by(desc(QueryHistory.created_at)).offset(offset).limit(limit)
    )
    queries = result.scalars().all()

    return {
        "success": True,
        "total": total,
        "data": [
            {
                "id": q.id,
                "user_id": q.user_id,
                "question": q.question,
                "category": q.category,
                "language": q.language,
                "confidence": q.confidence,
                "created_at": str(q.created_at),
            }
            for q in queries
        ],
    }


# ── DAILY STATS ───────────────────────────────────────────────────────────────

@router.get("/stats/daily", summary="Daily usage statistics")
async def daily_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Returns daily query counts for the last N days (for chart rendering)."""
    from sqlalchemy import cast, Date as SQLDate

    result = await db.execute(
        select(
            func.date(QueryHistory.created_at).label("date"),
            func.count(QueryHistory.id).label("queries"),
        )
        .where(QueryHistory.created_at >= datetime.now(timezone.utc) - timedelta(days=days))
        .group_by(func.date(QueryHistory.created_at))
        .order_by("date")
    )
    rows = result.all()

    return {
        "success": True,
        "days": days,
        "data": [{"date": str(row.date), "queries": row.queries} for row in rows],
    }


@router.get("/stats/schemes", summary="Scheme query statistics")
async def scheme_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Most queried categories and scheme-level stats."""
    result = await db.execute(
        select(
            QueryHistory.category,
            func.count(QueryHistory.id).label("total"),
            func.avg(QueryHistory.confidence).label("avg_confidence"),
        )
        .where(QueryHistory.category.isnot(None))
        .group_by(QueryHistory.category)
        .order_by(desc("total"))
    )
    rows = result.all()

    return {
        "success": True,
        "data": [
            {
                "category": row.category,
                "total_queries": row.total,
                "avg_confidence": round(float(row.avg_confidence or 0), 3),
            }
            for row in rows
        ],
    }
