"""
SevaSetu AI — Government Schemes API Router
Author: Rahul Jha | Made in India 🇮🇳

Endpoints:
  GET  /api/v1/schemes/             - List all schemes (filterable)
  GET  /api/v1/schemes/{id}         - Get scheme details
  POST /api/v1/schemes/eligibility  - Check user eligibility for schemes
  GET  /api/v1/schemes/categories   - Get scheme categories
  POST /api/v1/schemes/             - Admin: Create scheme
  PUT  /api/v1/schemes/{id}         - Admin: Update scheme
  DELETE /api/v1/schemes/{id}       - Admin: Delete scheme
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_admin_user
from app.models.user import User, Scheme, UserScheme, SchemeCategory, EligibilityStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# ── SCHEMAS ──────────────────────────────────────────────────────────────────

class SchemeCreate(BaseModel):
    name: str
    description: str
    category: SchemeCategory
    ministry: Optional[str] = None
    benefits: Optional[str] = None
    eligibility_text: Optional[str] = None
    eligibility_criteria: Optional[dict] = None
    required_documents: Optional[List[str]] = None
    application_url: Optional[str] = None
    helpline: Optional[str] = None
    application_steps: Optional[str] = None
    states_applicable: Optional[List[str]] = None
    max_income: Optional[float] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = "all"
    is_central: bool = True

class EligibilityCheckRequest(BaseModel):
    annual_income: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    caste_category: Optional[str] = None      # general | sc | st | obc
    is_farmer: Optional[bool] = False
    has_land: Optional[bool] = False
    land_hectares: Optional[float] = None
    is_student: Optional[bool] = False
    is_disabled: Optional[bool] = False
    has_house: Optional[bool] = True
    family_size: Optional[int] = None
    categories: Optional[List[str]] = None    # Filter by scheme category


# ── LIST SCHEMES ─────────────────────────────────────────────────────────────

@router.get("/", summary="List all government schemes")
async def list_schemes(
    category: Optional[str]  = None,
    search:   Optional[str]  = None,
    state:    Optional[str]  = None,
    is_central: Optional[bool] = None,
    page:  int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get paginated list of government schemes with optional filters.
    Supports search by name/description, category filter, state filter.
    """
    offset = (page - 1) * limit
    query = select(Scheme).where(Scheme.is_active == True)

    if category:
        query = query.where(Scheme.category == category)
    if state:
        query = query.where(
            or_(Scheme.states_applicable.is_(None),
                Scheme.states_applicable.contains([state]))
        )
    if is_central is not None:
        query = query.where(Scheme.is_central == is_central)
    if search:
        query = query.where(
            or_(
                Scheme.name.ilike(f"%{search}%"),
                Scheme.description.ilike(f"%{search}%"),
                Scheme.benefits.ilike(f"%{search}%"),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(query.offset(offset).limit(limit))
    schemes = result.scalars().all()

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "data": [_scheme_to_dict(s) for s in schemes],
    }


@router.get("/categories", summary="Get scheme categories with counts")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return all scheme categories and their scheme counts."""
    result = await db.execute(
        select(Scheme.category, func.count(Scheme.id).label("count"))
        .where(Scheme.is_active == True)
        .group_by(Scheme.category)
    )
    rows = result.all()

    category_icons = {
        "agriculture": "🌾", "health": "🏥", "education": "📚",
        "housing": "🏠", "women": "👩", "finance": "💰",
        "employment": "💼", "social": "🤝", "digital": "💻",
    }

    return {
        "success": True,
        "categories": [
            {
                "key": row.category,
                "label": row.category.replace("_", " ").title(),
                "icon": category_icons.get(row.category, "📋"),
                "count": row.count,
            }
            for row in rows
        ],
    }


@router.get("/{scheme_id}", summary="Get scheme details")
async def get_scheme(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get full details of a specific government scheme."""
    result = await db.execute(select(Scheme).where(Scheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    return {"success": True, "data": _scheme_to_dict(scheme, full=True)}


# ── ELIGIBILITY CHECK ─────────────────────────────────────────────────────────

@router.post("/eligibility", summary="Check scheme eligibility")
async def check_eligibility(
    request: EligibilityCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    AI-powered eligibility matching.
    Given user's profile data, returns matching schemes with eligibility scores.
    """
    query = select(Scheme).where(Scheme.is_active == True)
    if request.categories:
        query = query.where(Scheme.category.in_(request.categories))

    result = await db.execute(query)
    all_schemes = result.scalars().all()

    eligible_schemes = []

    for scheme in all_schemes:
        score, reasons = _calculate_eligibility(scheme, request)
        if score > 0.3:  # Only show schemes with >30% match
            # Save to user_schemes
            existing = await db.execute(
                select(UserScheme).where(
                    UserScheme.user_id == current_user.id,
                    UserScheme.scheme_id == scheme.id,
                )
            )
            user_scheme = existing.scalar_one_or_none()

            status_val = (
                EligibilityStatus.ELIGIBLE if score >= 0.7
                else EligibilityStatus.PARTIAL if score >= 0.4
                else EligibilityStatus.NOT_ELIGIBLE
            )

            if user_scheme:
                user_scheme.eligibility_score = score
                user_scheme.status = status_val
                user_scheme.notes = "; ".join(reasons)
            else:
                user_scheme = UserScheme(
                    user_id=current_user.id,
                    scheme_id=scheme.id,
                    eligibility_score=score,
                    status=status_val,
                    notes="; ".join(reasons),
                )
                db.add(user_scheme)

            eligible_schemes.append({
                **_scheme_to_dict(scheme),
                "eligibility_score": round(score, 2),
                "eligibility_status": status_val.value,
                "eligibility_reasons": reasons,
            })

    await db.commit()

    # Sort by score descending
    eligible_schemes.sort(key=lambda x: x["eligibility_score"], reverse=True)

    return {
        "success": True,
        "total_checked": len(all_schemes),
        "eligible_count": len([s for s in eligible_schemes if s["eligibility_score"] >= 0.7]),
        "schemes": eligible_schemes,
    }


# ── ADMIN: CREATE SCHEME ──────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED, summary="[Admin] Create scheme")
async def create_scheme(
    request: SchemeCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin only: Add a new government scheme to the database."""
    scheme = Scheme(**request.dict())
    db.add(scheme)
    await db.commit()
    await db.refresh(scheme)
    logger.info(f"✅ New scheme created by admin {admin.email}: {scheme.name}")
    return {"success": True, "message": "Scheme created", "data": _scheme_to_dict(scheme)}


@router.put("/{scheme_id}", summary="[Admin] Update scheme")
async def update_scheme(
    scheme_id: int,
    request: SchemeCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin only: Update an existing scheme."""
    result = await db.execute(select(Scheme).where(Scheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(scheme, key, value)

    await db.commit()
    logger.info(f"✅ Scheme {scheme_id} updated by admin {admin.email}")
    return {"success": True, "message": "Scheme updated", "data": _scheme_to_dict(scheme)}


@router.delete("/{scheme_id}", summary="[Admin] Delete scheme")
async def delete_scheme(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Admin only: Soft-delete a scheme (set is_active=False)."""
    result = await db.execute(select(Scheme).where(Scheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme.is_active = False
    await db.commit()
    logger.info(f"🗑️ Scheme {scheme_id} deactivated by admin {admin.email}")
    return {"success": True, "message": "Scheme deactivated"}


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _scheme_to_dict(scheme: Scheme, full: bool = False) -> dict:
    """Serialize Scheme model to dict."""
    data = {
        "id": scheme.id,
        "name": scheme.name,
        "short_name": scheme.short_name,
        "description": scheme.description,
        "category": scheme.category.value if scheme.category else None,
        "ministry": scheme.ministry,
        "benefits": scheme.benefits,
        "is_central": scheme.is_central,
        "is_active": scheme.is_active,
        "application_url": scheme.application_url,
        "helpline": scheme.helpline,
    }
    if full:
        data.update({
            "eligibility_text": scheme.eligibility_text,
            "eligibility_criteria": scheme.eligibility_criteria,
            "required_documents": scheme.required_documents,
            "application_steps": scheme.application_steps,
            "states_applicable": scheme.states_applicable,
            "max_income": scheme.max_income,
            "min_age": scheme.min_age,
            "max_age": scheme.max_age,
            "gender": scheme.gender,
        })
    return data


def _calculate_eligibility(scheme: Scheme, req: EligibilityCheckRequest) -> tuple:
    """
    Rule-based eligibility scoring engine.
    Returns (score: float 0-1, reasons: list[str])
    """
    score = 0.5   # Base score — assume partially eligible
    reasons = []
    criteria = scheme.eligibility_criteria or {}

    # Income check
    if scheme.max_income and req.annual_income:
        if req.annual_income <= scheme.max_income:
            score += 0.2
            reasons.append(f"✅ Income ₹{req.annual_income:,.0f} ≤ limit ₹{scheme.max_income:,.0f}")
        else:
            score -= 0.4
            reasons.append(f"❌ Income ₹{req.annual_income:,.0f} exceeds limit ₹{scheme.max_income:,.0f}")

    # Age check
    if scheme.min_age and req.age:
        if req.age < scheme.min_age:
            score -= 0.3
            reasons.append(f"❌ Age {req.age} < minimum {scheme.min_age}")
        else:
            score += 0.1
            reasons.append(f"✅ Age {req.age} meets minimum {scheme.min_age}")

    if scheme.max_age and req.age:
        if req.age > scheme.max_age:
            score -= 0.3
            reasons.append(f"❌ Age {req.age} > maximum {scheme.max_age}")
        else:
            score += 0.1

    # Gender check
    if scheme.gender and scheme.gender != "all" and req.gender:
        if req.gender.lower() == scheme.gender.lower():
            score += 0.1
            reasons.append(f"✅ Gender matches ({scheme.gender})")
        else:
            score -= 0.5
            reasons.append(f"❌ Scheme is for {scheme.gender} only")

    # Farmer-specific schemes
    if scheme.category == SchemeCategory.AGRICULTURE:
        if req.is_farmer:
            score += 0.2
            reasons.append("✅ You are a farmer — eligible for agriculture schemes")
        else:
            score -= 0.2

    # Clamp score to [0, 1]
    score = max(0.0, min(1.0, score))
    return score, reasons
