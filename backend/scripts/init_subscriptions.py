import asyncio
import motor.motor_asyncio
from datetime import datetime
import sys
import os

# Add parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


async def init_subscription_tiers():
    """初始化套餐配置"""
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    tiers = [
        {
            "_id": "tier_monthly",
            "name": "月度套餐",
            "type": "monthly",
            "price": 2900,  # 29元
            "duration_days": 30,
            "credits_per_month": 50,
            "description": "每月50点，适合轻度使用",
            "features": [
                "每月50点生成额度",
                "音色克隆功能",
                "3分钟音频生成",
                "历史记录保存"
            ],
            "is_active": True
        },
        {
            "_id": "tier_quarterly",
            "name": "季度套餐",
            "type": "quarterly",
            "price": 7900,  # 79元
            "duration_days": 90,
            "credits_per_month": 60,
            "description": "每月60点，季度订阅更优惠",
            "features": [
                "每月60点生成额度",
                "音色克隆功能",
                "5分钟音频生成",
                "优先生成队列",
                "历史记录永久保存"
            ],
            "is_active": True
        },
        {
            "_id": "tier_yearly",
            "name": "年度套餐",
            "type": "yearly",
            "price": 29900,  # 299元
            "duration_days": 365,
            "credits_per_month": 80,
            "description": "每月80点，年度订阅最划算",
            "features": [
                "每月80点生成额度",
                "音色克隆功能",
                "10分钟音频生成",
                "VIP优先生成队列",
                "历史记录永久保存",
                "专属客服支持"
            ],
            "is_active": True
        }
    ]

    for tier in tiers:
        await db.subscription_tiers.update_one(
            {"_id": tier["_id"]},
            {"$set": tier},
            upsert=True
        )
        print(f"Created/Updated tier: {tier['name']}")

    print("\nSubscription tiers initialized!")


if __name__ == "__main__":
    asyncio.run(init_subscription_tiers())