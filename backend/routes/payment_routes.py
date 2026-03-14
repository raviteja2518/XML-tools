from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/api/payment", tags=["Payment"])

@router.post("/checkout", response_model=schemas.UserResponse)
def mock_checkout(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.has_paid = 1
    db.commit()
    db.refresh(user)
    return user
