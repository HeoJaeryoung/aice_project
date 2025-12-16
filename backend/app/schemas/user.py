from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Request schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Response schemas
class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    is_active: bool
    is_verified: bool
    subscription_tier: str
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
