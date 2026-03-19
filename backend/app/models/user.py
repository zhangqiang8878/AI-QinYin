from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    phone: str
    nickname: Optional[str] = "准妈妈"
    avatar_url: Optional[str] = None
    pregnancy_weeks: Optional[int] = None
    expected_due_date: Optional[datetime] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    pregnancy_weeks: Optional[int] = None
    expected_due_date: Optional[datetime] = None


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    last_login: datetime
    role: UserRole = UserRole.USER
    is_active: bool = True

    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    id: str
    created_at: datetime
    pregnancy_weeks: Optional[int] = None


class UserCredits(BaseModel):
    credits: int
    free_credits_used: int
    free_credits_total: int = 3