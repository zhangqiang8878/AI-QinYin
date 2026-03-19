from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
import uuid

from app.database import get_database
from app.models.payment import OrderCreate, OrderType, PaymentStatus
from app.services.wechat_pay import wechat_pay_service
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/orders")
async def create_order(
    req: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建支付订单"""
    db = get_database()

    # Generate order number
    order_no = f"QYY{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

    # Get user openid (should be stored during login)
    user = await db.users.find_one({"_id": current_user["sub"]})
    openid = user.get("openid")

    if not openid:
        raise HTTPException(status_code=400, detail="WeChat openid not found")

    # Calculate amount and description based on order type
    if req.type == OrderType.SUBSCRIPTION:
        if not req.tier_id:
            raise HTTPException(status_code=400, detail="Tier ID required")

        tier = await db.subscription_tiers.find_one({"_id": req.tier_id})
        if not tier:
            raise HTTPException(status_code=404, detail="Subscription tier not found")

        amount = tier["price"]
        description = f"{tier['name']}订阅"
    elif req.type == OrderType.CREDITS:
        # Credits pack pricing
        credit_packs = {
            10: 500,   # 10 credits = 5 yuan
            50: 2000,  # 50 credits = 20 yuan
            100: 3500  # 100 credits = 35 yuan
        }
        credits = req.credits_amount or 10
        amount = credit_packs.get(credits, 500)
        description = f"{credits}点数充值"
    else:
        raise HTTPException(status_code=400, detail="Invalid order type")

    # Create order in DB
    order_doc = {
        "user_id": current_user["sub"],
        "order_no": order_no,
        "type": req.type,
        "amount": amount,
        "status": PaymentStatus.PENDING,
        "tier_id": req.tier_id,
        "credits_amount": req.credits_amount,
        "created_at": datetime.utcnow()
    }

    await db.orders.insert_one(order_doc)

    # Create WeChat Pay order
    try:
        pay_result = await wechat_pay_service.create_order(
            order_no=order_no,
            amount=amount,
            description=description,
            openid=openid
        )

        # Update order with prepay_id
        await db.orders.update_one(
            {"order_no": order_no},
            {"$set": {"wechat_prepay_id": pay_result["prepay_id"]}}
        )

        return {
            "success": True,
            "data": {
                "order_no": order_no,
                "amount": amount,
                "pay_params": pay_result["pay_params"]
            }
        }

    except Exception as e:
        # Update order status to failed
        await db.orders.update_one(
            {"order_no": order_no},
            {"$set": {"status": PaymentStatus.FAILED}}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify")
async def payment_notify(request: Request):
    """微信支付回调通知"""
    xml_data = await request.body()

    result = wechat_pay_service.verify_notify(xml_data.decode())
    if not result:
        return "<xml><return_code><![CDATA[FAIL]]></return_code></xml>"

    if result.get("result_code") == "SUCCESS":
        order_no = result.get("out_trade_no")
        transaction_id = result.get("transaction_id")

        db = get_database()

        # Update order status
        await db.orders.update_one(
            {"order_no": order_no},
            {
                "$set": {
                    "status": PaymentStatus.SUCCESS,
                    "paid_at": datetime.utcnow()
                }
            }
        )

        # TODO: Grant credits or subscription to user

    return "<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>"