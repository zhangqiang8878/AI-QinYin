from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ContentType(str, Enum):
    STORY = "story"
    MUSIC = "music"
    POETRY = "poetry"


class ContentStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentCreate(BaseModel):
    type: ContentType
    voice_id: str
    theme: Optional[str] = None
    duration: Optional[int] = 3  # minutes


class ContentInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    voice_id: str
    type: ContentType
    theme: Optional[str] = None
    title: str
    text_content: str
    oss_url: Optional[str] = None
    duration: Optional[float] = None
    status: ContentStatus
    credits_used: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ContentResponse(BaseModel):
    id: str
    type: ContentType
    title: str
    oss_url: Optional[str] = None
    duration: Optional[float] = None
    status: ContentStatus
    created_at: datetime