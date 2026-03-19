from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class VoiceStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


class VoiceBase(BaseModel):
    name: str
    is_default: bool = False


class VoiceCreate(VoiceBase):
    pass


class VoiceUpdate(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None


class VoiceInDB(VoiceBase):
    id: str = Field(alias="_id")
    user_id: str
    voice_id: str  # TTS service voice ID
    oss_url: str
    duration: float
    status: VoiceStatus
    created_at: datetime
    last_used: Optional[datetime] = None
    access_count: int = 0

    class Config:
        populate_by_name = True


class VoiceResponse(VoiceBase):
    id: str
    voice_id: str
    duration: float
    status: VoiceStatus
    created_at: datetime
    oss_url: str