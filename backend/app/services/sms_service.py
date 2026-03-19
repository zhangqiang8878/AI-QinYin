import random
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from alibabacloud_dysmsapi20170525.client import Client
from alibabacloud_dysmsapi20170525.models import SendSmsRequest
from alibabacloud_tea_openapi.models import Config as AliyunConfig

from app.config import settings
from app.redis_client import redis_client


@dataclass
class SMSResult:
    success: bool
    message: str
    code: Optional[str] = None


class SMSService:
    def __init__(self):
        self.client = None
        if settings.SMS_ACCESS_KEY_ID and settings.SMS_ACCESS_KEY_SECRET:
            config = AliyunConfig(
                access_key_id=settings.SMS_ACCESS_KEY_ID,
                access_key_secret=settings.SMS_ACCESS_KEY_SECRET,
                endpoint="dysmsapi.aliyuncs.com"
            )
            self.client = Client(config)

    def generate_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join(random.choices('0123456789', k=6))

    def check_rate_limit(self, phone: str) -> bool:
        """检查发送频率限制"""
        minute_key = f"sms_limit:minute:{phone}"
        hour_key = f"sms_limit:hour:{phone}"
        day_key = f"sms_limit:day:{phone}"

        # Check minute limit
        if redis_client.get(minute_key):
            return False

        # Check hour limit
        hour_count = redis_client.get(hour_key)
        if hour_count and int(hour_count) >= settings.SMS_RATE_LIMIT_PER_HOUR:
            return False

        # Check day limit
        day_count = redis_client.get(day_key)
        if day_count and int(day_count) >= settings.SMS_RATE_LIMIT_PER_DAY:
            return False

        return True

    def _update_rate_limit(self, phone: str):
        """更新频率限制计数器"""
        minute_key = f"sms_limit:minute:{phone}"
        hour_key = f"sms_limit:hour:{phone}"
        day_key = f"sms_limit:day:{phone}"

        pipe = redis_client.pipeline()
        pipe.setex(minute_key, 60, "1")
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)
        pipe.incr(day_key)
        pipe.expire(day_key, 86400)
        pipe.execute()

    def send_code(self, phone: str) -> SMSResult:
        """发送验证码"""
        # Check rate limit
        if not self.check_rate_limit(phone):
            return SMSResult(
                success=False,
                message="发送过于频繁，请稍后再试"
            )

        # Generate code
        code = self.generate_code()

        # Store in Redis (5 minutes expiry)
        redis_client.setex(f"sms_code:{phone}", 300, code)

        # If no SMS client configured (dev mode), just return success
        if not self.client:
            return SMSResult(
                success=True,
                message="验证码已发送 (开发模式)",
                code=code  # Return code in dev mode for testing
            )

        try:
            # Send via Aliyun SMS
            request = SendSmsRequest(
                phone_numbers=phone,
                sign_name=settings.SMS_SIGN_NAME,
                template_code=settings.SMS_TEMPLATE_CODE,
                template_param=json.dumps({"code": code})
            )
            response = self.client.send_sms(request)

            if response.body.code == "OK":
                self._update_rate_limit(phone)
                return SMSResult(success=True, message="验证码已发送")
            else:
                return SMSResult(
                    success=False,
                    message=f"发送失败: {response.body.message}"
                )

        except Exception as e:
            return SMSResult(success=False, message=f"发送异常: {str(e)}")

    def verify_code(self, phone: str, code: str) -> bool:
        """验证验证码"""
        stored_code = redis_client.get(f"sms_code:{phone}")
        if not stored_code:
            return False

        if stored_code.upper() == code.upper():
            redis_client.delete(f"sms_code:{phone}")
            return True

        return False


sms_service = SMSService()