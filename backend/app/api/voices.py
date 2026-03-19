from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime

from app.database import get_database
from app.models.voice import VoiceCreate, VoiceUpdate, VoiceResponse, VoiceStatus
from app.services.oss_service import oss_service
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_voices(current_user: dict = Depends(get_current_user)):
    """获取用户音色列表"""
    db = get_database()
    voices = await db.voices.find(
        {"user_id": current_user["sub"]}
    ).sort("created_at", -1).to_list(length=None)

    return {
        "success": True,
        "data": [
            {
                "id": str(v["_id"]),
                "name": v["name"],
                "voice_id": v["voice_id"],
                "duration": v["duration"],
                "status": v["status"],
                "created_at": v["created_at"],
                "oss_url": v["oss_url"]
            }
            for v in voices
        ]
    }


@router.post("/")
async def create_voice(
    voice: VoiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建音色记录（上传完成后调用）.
    实际流程：1. 获取上传URL -> 2. 前端直传OSS -> 3. 调用此接口创建记录
    """
    db = get_database()

    # TODO: Call TTS service to clone voice
    # For now, create pending record
    voice_doc = {
        "user_id": current_user["sub"],
        "name": voice.name,
        "is_default": voice.is_default,
        "voice_id": None,  # Will be set after cloning
        "oss_url": "",  # Will be set after upload
        "duration": 0,
        "status": VoiceStatus.UPLOADED,
        "created_at": datetime.utcnow(),
        "last_used": None,
        "access_count": 0
    }

    result = await db.voices.insert_one(voice_doc)

    return {
        "success": True,
        "data": {
            "id": str(result.inserted_id),
            "name": voice.name,
            "status": VoiceStatus.UPLOADED
        }
    }


@router.post("/upload-url")
async def get_upload_url(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """获取OSS直传URL"""
    try:
        url_info = oss_service.generate_upload_url(
            current_user["sub"],
            "voices",
            filename
        )
        return {"success": True, "data": url_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """删除音色"""
    db = get_database()

    # Find voice
    voice = await db.voices.find_one({
        "_id": voice_id,
        "user_id": current_user["sub"]
    })

    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Delete from DB
    await db.voices.delete_one({"_id": voice_id})

    return {"success": True, "data": {"message": "Voice deleted"}}