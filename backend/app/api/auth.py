"""
SevaSetu AI — Authentication API Router
Author: Rahul Jha | Made in India 🇮🇳

Endpoints:
  POST /api/v1/auth/register   - New user registration
  POST /api/v1/auth/login      - Login, get JWT
  POST /api/v1/auth/refresh    - Refresh access token
  POST /api/v1/auth/logout     - Logout (client-side token discard)
  GET  /api/v1/auth/me         - Get current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import logging
import re

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_current_active_user, decode_token,
)
from app.models.user import User, UserRole, PasswordResetToken
from app.services.email_service import send_welcome_email, send_password_reset_email

logger = logging.getLogger(__name__)
router = APIRouter()


# ── REQUEST / RESPONSE SCHEMAS ───────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    state: str
    language: Optional[str] = "en"

    @validator("mobile")
    def validate_mobile(cls, v):
        if not re.match(r"^[6-9]\d{9}$", v.replace("+91", "").replace(" ", "")):
            raise ValueError("Invalid Indian mobile number")
        return v.replace("+91", "").replace(" ", "")

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @validator("name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip().title()


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register new user")
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new SevaSetu AI user.

    - Validates email and mobile uniqueness
    - Hashes password with bcrypt
    - Returns JWT access + refresh tokens
    - Sends welcome email in background
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login or use a different email.",
        )

    # Check if mobile already exists
    result = await db.execute(select(User).where(User.mobile == request.mobile))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mobile number already registered.",
        )

    # Create user
    user = User(
        name=request.name,
        email=request.email,
        mobile=request.mobile,
        password_hash=hash_password(request.password),
        state=request.state,
        language=request.language,
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(user.id)

    # Send welcome email in background (non-blocking)
    background_tasks.add_task(send_welcome_email, user.email, user.name, user.language)

    logger.info(f"✅ New user registered: {user.email} | State: {user.state}")

    return {
        "success": True,
        "message": f"🙏 Welcome to SevaSetu AI, {user.name}! Your account is ready.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,  # 24 hours in seconds
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "state": user.state,
            "role": user.role.value,
            "language": user.language,
        },
    }


@router.post("/login", response_model=LoginResponse, summary="User login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email/mobile + password.
    Returns JWT Bearer token (valid 24h) and refresh token (valid 30d).
    """
    # Find user by email or mobile
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username) | (User.mobile == form_data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"⚠️ Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/mobile or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated. Contact support at support@sevasetu.ai",
        )

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(user.id)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info(f"✅ User logged in: {user.email} | Role: {user.role.value}")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=86400,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "state": user.state,
            "role": user.role.value,
            "language": user.language,
        },
    )


@router.post("/refresh", summary="Refresh access token")
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Use a valid refresh token to get a new access token."""
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = int(payload["sub"])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        new_access_token = create_access_token({"sub": str(user.id), "role": user.role.value})

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 86400,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout", summary="Logout user")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint. JWT tokens are stateless, so client should discard the token.
    In production, implement a token blacklist using Redis.
    """
    logger.info(f"👋 User logged out: {current_user.email}")
    return {
        "success": True,
        "message": "Logged out successfully. Please discard your token.",
    }


@router.get("/me", summary="Get current user profile")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get the currently authenticated user's profile."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "mobile": current_user.mobile,
        "state": current_user.state,
        "role": current_user.role.value,
        "language": current_user.language,
        "is_active": current_user.is_active,
        "created_at": str(current_user.created_at),
    }


@router.post("/forgot-password", summary="Request password reset")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send a short-lived password reset link without revealing whether an email exists."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return the same response to prevent account enumeration.
    generic = {
        "success": True,
        "message": "If an account exists for this email, a password reset link has been sent."
    }
    if not user or not user.is_active:
        return generic

    await db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    db.add(reset_token)
    await db.commit()

    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
    background_tasks.add_task(send_password_reset_email, user.email, user.name, reset_url)
    logger.info("🔐 Password reset requested for user: %s", user.email)
    return generic


@router.post("/reset-password", summary="Reset password with token")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Consume a valid, single-use reset token and set a new password."""
    token_hash = hashlib.sha256(request.token.encode("utf-8")).hexdigest()
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    reset_token = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    expires_at = reset_token.expires_at if reset_token else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not reset_token or reset_token.used_at is not None or expires_at <= now:
        raise HTTPException(status_code=400, detail="This password reset link is invalid or has expired.")

    user_result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Unable to reset password for this account.")

    user.password_hash = hash_password(request.new_password)
    reset_token.used_at = now
    await db.commit()
    logger.info("🔒 Password reset completed for user: %s", user.email)
    return {"success": True, "message": "Password reset successfully. Please sign in with your new password."}


@router.post("/change-password", summary="Change password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change authenticated user's password."""
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    current_user.password_hash = hash_password(request.new_password)
    await db.commit()

    logger.info(f"🔒 Password changed for user: {current_user.email}")
    return {"success": True, "message": "Password changed successfully"}
