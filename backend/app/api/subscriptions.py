from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta

from app.database import get_database
from app.models.subscription import SubscriptionTier, SubscriptionResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_subscription_tiers():
    """获取套餐列表"""
    db = get_database()
    tiers = await db.subscription_tiers.find(
        {"is_active": True}
    ).sort("price", 1).to_list(length=None)

    return {
        "success": True,
        "data": [
            {
                "id": str(t["_id"]),
                "name": t["name"],
                "type": t["type"],
                "price": t["price"],
                "duration_days": t["duration_days"],
                "credits_per_month": t["credits_per_month"],
                "description": t["description"],
                "features": t.get("features", [])
            }
            for t in tiers
        ]
    }


@router.get("/my")
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """获取当前用户订阅"""
    db = get_database()
    sub = await db.user_subscriptions.find_one({
        "user_id": current_user["sub"],
        "is_active": True,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not sub:
        return {
            "success": True,
            "data": None
        }

    return {
        "success": True,
        "data": {
            "id": str(sub["_id"]),
            "tier_name": sub["tier_name"],
            "started_at": sub["started_at"],
            "expires_at": sub["expires_at"],
            "credits_remaining": sub["credits_remaining"],
            "auto_renew": sub.get("auto_renew", False)
        }
    }