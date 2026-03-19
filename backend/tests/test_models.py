import pytest
from datetime import datetime
from app.models.user import UserCreate, UserInDB, UserRole
from app.models.voice import VoiceCreate, VoiceStatus
from app.models.content import ContentCreate, ContentType


def test_user_create():
    user = UserCreate(phone="13800138000", nickname="Test User")
    assert user.phone == "13800138000"
    assert user.nickname == "Test User"


def test_user_default_values():
    user = UserCreate(phone="13800138000")
    assert user.nickname == "准妈妈"


def test_voice_create():
    voice = VoiceCreate(name="爸爸的声音", is_default=True)
    assert voice.name == "爸爸的声音"
    assert voice.is_default is True


def test_content_create():
    content = ContentCreate(type=ContentType.STORY, voice_id="voice_123")
    assert content.type == ContentType.STORY
    assert content.voice_id == "voice_123"
    assert content.duration == 3  # default