"""SevaSetu AI — Users API | Rahul Jha | Made in India 🇮🇳"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = None

@router.put("/me", summary="Update profile")
async def update_profile(request: UpdateProfileRequest, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if request.name: current_user.name = request.name
    if request.state: current_user.state = request.state
    if request.language: current_user.language = request.language
    await db.commit()
    return {"success": True, "message": "Profile updated"}

@router.patch("/me/language", summary="Update language preference")
async def update_language(language: str, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if language not in ["en", "hi", "mr"]:
        from fastapi import HTTPException
        raise HTTPException(400, "Unsupported language. Use: en, hi, mr")
    current_user.language = language
    await db.commit()
    return {"success": True, "language": language}
