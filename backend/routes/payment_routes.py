from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
from database import get_db
from models import User
from schemas import UserResponse
from dependencies import get_current_active_user

router = APIRouter(prefix="/api/payment", tags=["Payment"])

@router.post("/checkout", response_model=UserResponse)
async def mock_checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    current_user.has_paid = 1
    current_user.role = "subscriber"
    # Set expiry to 30 days from now
    current_user.subscription_expiry = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/upgrade", response_model=UserResponse)
async def upgrade_to_subscriber(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would redirect to a payment checkout
    # For this mock, we just upgrade them immediately
    current_user.has_paid = 1
    current_user.role = "subscriber"
    current_user.requested_role = "subscriber"
    # Set expiry to 30 days from now
    current_user.subscription_expiry = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
