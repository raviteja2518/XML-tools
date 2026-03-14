from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
from database import get_db
from models import User
from schemas import UserResponse, PlanRequest
from dependencies import get_current_active_user

router = APIRouter(prefix="/api/payment", tags=["Payment"])

def calculate_expiry(months: int):
    days = 30
    if months == 6:
        days = 180
    elif months == 12:
        days = 365
    return datetime.datetime.utcnow() + datetime.timedelta(days=days)

@router.post("/checkout", response_model=UserResponse)
async def mock_checkout(
    plan: PlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if plan.plan_type not in [1, 6, 12]:
        raise HTTPException(status_code=400, detail="Invalid plan type")
        
    current_user.has_paid = 1
    current_user.role = "subscriber"
    current_user.subscription_expiry = calculate_expiry(plan.plan_type)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/upgrade", response_model=UserResponse)
async def upgrade_to_subscriber(
    plan: PlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if plan.plan_type not in [1, 6, 12]:
        raise HTTPException(status_code=400, detail="Invalid plan type")

    current_user.has_paid = 1
    current_user.role = "subscriber"
    current_user.requested_role = "subscriber"
    current_user.subscription_expiry = calculate_expiry(plan.plan_type)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
