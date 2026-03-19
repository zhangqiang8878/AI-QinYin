import asyncio
import motor.motor_asyncio
from datetime import datetime
import sys
import os

# Add parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


async def create_indexes():
    """创建MongoDB索引"""
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    # Users collection
    await db.users.create_index("phone", unique=True)
    await db.users.create_index("created_at")
    print("Created users indexes")

    # Voices collection
    await db.voices.create_index("user_id")
    await db.voices.create_index("voice_id")
    print("Created voices indexes")

    # Subscriptions collection
    await db.user_subscriptions.create_index("user_id")
    await db.user_subscriptions.create_index([("user_id", 1), ("expires_at", -1)])
    await db.user_subscriptions.create_index("expires_at")
    print("Created subscriptions indexes")

    # Orders collection
    await db.orders.create_index("user_id")
    await db.orders.create_index("order_no", unique=True)
    await db.orders.create_index("created_at")
    print("Created orders indexes")

    # Contents collection
    await db.contents.create_index("user_id")
    await db.contents.create_index("created_at")
    print("Created contents indexes")


if __name__ == "__main__":
    asyncio.run(create_indexes())