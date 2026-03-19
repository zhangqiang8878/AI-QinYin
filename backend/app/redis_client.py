import redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)


def get_redis():
    return redis_client


def set_sms_code(phone: str, code: str, expire: int = 300):
    """存储验证码，默认5分钟过期"""
    redis_client.setex(f"sms_code:{phone}", expire, code)


def get_sms_code(phone: str) -> str:
    return redis_client.get(f"sms_code:{phone}")


def delete_sms_code(phone: str):
    redis_client.delete(f"sms_code:{phone}")


def check_sms_rate_limit(phone: str) -> bool:
    """检查短信发送频率限制"""
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

    # Update counters
    pipe = redis_client.pipeline()
    pipe.setex(minute_key, 60, "1")
    pipe.incr(hour_key)
    pipe.expire(hour_key, 3600)
    pipe.incr(day_key)
    pipe.expire(day_key, 86400)
    pipe.execute()

    return True