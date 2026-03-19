from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SubscriptionType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionTier(BaseModel):
    id: str = Field(alias="_id")
    name: str
    type: SubscriptionType
    price: int  # 分
    duration_days: int
    credits_per_month: int
    description: str
    features: List[str]
    is_active: bool = True

    class Config:
        populate_by_name = True


class UserSubscription(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    tier_id: str
    tier_name: str
    started_at: datetime
    expires_at: datetime
    credits_remaining: int
    is_active: bool = True
    auto_renew: bool = False

    class Config:
        populate_by_name = True


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    type: SubscriptionType
    price: int
    duration_days: int
    credits_per_month: int
    description: str
    features: List[str]