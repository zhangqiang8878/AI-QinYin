from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.utils.auth import create_access_token
from app.services.sms_service import sms_service

router = APIRouter()


class SendCodeRequest(BaseModel):
    phone: str


class LoginRequest(BaseModel):
    phone: str
    code: str


class LoginResponse(BaseModel):
    token: str
    user: dict


@router.post("/sms-code")
async def send_sms_code(req: SendCodeRequest):
    """发送短信验证码"""
    result = sms_service.send_code(req.phone)
    if result.success:
        return {"success": True, "data": {"message": result.message}}
    else:
        raise HTTPException(status_code=429, detail=result.message)


@router.post("/login")
async def login(req: LoginRequest):
    """登录/注册"""
    # Verify SMS code
    if not sms_service.verify_code(req.phone, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # TODO: Create or get user from database
    # For now, mock user
    user = {
        "id": "user_123",
        "phone": req.phone,
        "nickname": "准妈妈"
    }

    token = create_access_token({"sub": user["id"], "phone": user["phone"]})

    return {
        "success": True,
        "data": {
            "token": token,
            "user": user
        }
    }