from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password_hash = Column(String)
    role = Column(String, default="pending")  # pending, employee, subscriber, admin
    requested_role = Column(String, default="employee") # what the user chose during registration
    has_paid = Column(Integer, default=0) # SQLite boolean equivalent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
