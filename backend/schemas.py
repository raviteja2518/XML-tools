from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    requested_role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    requested_role: str
    has_paid: int
    profile_picture: Optional[str] = None
    subscription_expiry: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    requested_role: Optional[str] = None

class PlanRequest(BaseModel):
    plan_type: int  # 1, 6, or 12 months

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
