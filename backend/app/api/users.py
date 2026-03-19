from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.database import get_database
from app.models.user import UserUpdate, UserResponse, UserCredits
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    db = get_database()
    user = await db.users.find_one({"_id": current_user["sub"]})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "data": {
            "id": str(user["_id"]),
            "phone": user["phone"],
            "nickname": user.get("nickname", "准妈妈"),
            "pregnancy_weeks": user.get("pregnancy_weeks"),
            "created_at": user["created_at"]
        }
    }


@router.put("/me")
async def update_user_info(
    update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新用户信息"""
    db = get_database()

    update_data = update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.users.update_one(
        {"_id": current_user["sub"]},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "data": {"message": "Updated successfully"}}


@router.get("/credits")
async def get_user_credits(current_user: dict = Depends(get_current_user)):
    """获取用户点数"""
    db = get_database()
    user = await db.users.find_one({"_id": current_user["sub"]})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "data": {
            "credits": user.get("credits", 0),
            "free_credits_used": user.get("free_credits_used", 0),
            "free_credits_total": 3
        }
    }