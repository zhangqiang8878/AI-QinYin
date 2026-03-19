from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.database import get_database
from app.models.content import ContentCreate, ContentType, ContentStatus
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_contents(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """获取用户生成历史"""
    db = get_database()

    skip = (page - 1) * limit
    contents = await db.contents.find(
        {"user_id": current_user["sub"]}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)

    total = await db.contents.count_documents({"user_id": current_user["sub"]})

    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": str(c["_id"]),
                    "type": c["type"],
                    "title": c["title"],
                    "oss_url": c.get("oss_url"),
                    "duration": c.get("duration"),
                    "status": c["status"],
                    "created_at": c["created_at"]
                }
                for c in contents
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    }


@router.post("/")
async def create_content(
    req: ContentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    创建内容生成任务.
    流程: 1. 验证用户点数 -> 2. 扣除点数 -> 3. 调用TTS -> 4. 返回任务ID
    """
    db = get_database()

    # Check user credits
    user = await db.users.find_one({"_id": current_user["sub"]})
    credits = user.get("credits", 0)

    if credits < 1:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    # Check voice
    voice = await db.voices.find_one({
        "voice_id": req.voice_id,
        "user_id": current_user["sub"]
    })

    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Generate content text (mock - should use LLM)
    content_titles = {
        ContentType.STORY: "睡前故事",
        ContentType.MUSIC: "胎教音乐",
        ContentType.POETRY: "古典诗词"
    }

    title = f"{content_titles.get(req.type, '内容')} - {datetime.now().strftime('%m月%d日')}"
    text_content = f"这是一个示例{content_titles.get(req.type, '内容')}文本。" * 10

    # Create content record
    content_doc = {
        "user_id": current_user["sub"],
        "voice_id": req.voice_id,
        "type": req.type,
        "theme": req.theme,
        "title": title,
        "text_content": text_content,
        "oss_url": None,
        "duration": None,
        "status": ContentStatus.PENDING,
        "credits_used": 1,
        "created_at": datetime.utcnow(),
        "completed_at": None
    }

    result = await db.contents.insert_one(content_doc)
    content_id = str(result.inserted_id)

    # Deduct credits
    await db.users.update_one(
        {"_id": current_user["sub"]},
        {"$inc": {"credits": -1}}
    )

    # TODO: Trigger async TTS synthesis
    # For now, return immediately

    return {
        "success": True,
        "data": {
            "id": content_id,
            "title": title,
            "status": ContentStatus.PENDING
        }
    }


@router.get("/{content_id}")
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取内容详情"""
    db = get_database()

    content = await db.contents.find_one({
        "_id": content_id,
        "user_id": current_user["sub"]
    })

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return {
        "success": True,
        "data": {
            "id": str(content["_id"]),
            "type": content["type"],
            "title": content["title"],
            "text_content": content["text_content"],
            "oss_url": content.get("oss_url"),
            "duration": content.get("duration"),
            "status": content["status"],
            "created_at": content["created_at"],
            "completed_at": content.get("completed_at")
        }
    }