from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from dependencies import get_current_active_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])

UPLOAD_DIR = "uploads/profile_pictures"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/update", response_model=UserResponse)
async def update_profile(
    obj_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if obj_in.name is not None:
        current_user.name = obj_in.name
    if obj_in.phone is not None:
        current_user.phone = obj_in.phone
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
