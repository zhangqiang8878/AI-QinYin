from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderType(str, Enum):
    SUBSCRIPTION = "subscription"
    CREDITS = "credits"


class OrderCreate(BaseModel):
    type: OrderType
    tier_id: Optional[str] = None
    credits_amount: Optional[int] = None


class OrderInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    order_no: str
    type: OrderType
    amount: int  # 分
    status: PaymentStatus
    tier_id: Optional[str] = None
    credits_amount: Optional[int] = None
    wechat_prepay_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


class PaymentNotify(BaseModel):
    appid: str
    mch_id: str
    out_trade_no: str
    transaction_id: str
    total_fee: int
    result_code: str