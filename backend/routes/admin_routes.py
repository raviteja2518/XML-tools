from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from dependencies import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)])

@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Fetch all users (pending, employee, subscriber, admin)"""
    users = db.query(models.User).all()
    return users

@router.put("/users/{user_id}/approve", response_model=schemas.UserResponse)
def approve_user(user_id: int, role: str, db: Session = Depends(get_db)):
    """Approve a user by passing ?role=employee or ?role=subscriber"""
    if role not in ["employee", "subscriber"]:
        raise HTTPException(status_code=400, detail="Role must be 'employee' or 'subscriber'")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.role = role
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def edit_user(user_id: int, user_update: schemas.UserCreate, db: Session = Depends(get_db)):
    """Edit user details (can only edit name, email, phone from admin UI easily)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.name = user_update.name
    user.email = user_update.email
    user.phone = user_update.phone
    
    # Only update password if provided
    if user_update.password:
        from auth import get_password_hash
        user.password_hash = get_password_hash(user_update.password)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user account"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
