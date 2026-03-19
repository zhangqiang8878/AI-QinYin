from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_qinyin"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7 days

    # Aliyun SMS
    SMS_ACCESS_KEY_ID: str = ""
    SMS_ACCESS_KEY_SECRET: str = ""
    SMS_SIGN_NAME: str = "AI亲音"
    SMS_TEMPLATE_CODE: str = "SMS_12345678"

    # Aliyun OSS
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-beijing.aliyuncs.com"
    OSS_BUCKET_NAME: str = "ai-qinyin-audio"
    OSS_EXPIRE_SECONDS: int = 3600

    # WeChat Pay
    WECHAT_APPID: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = "https://your-api-domain.com/api/payments/notify"

    # TTS Service
    TTS_SERVICE_URL: str = "http://localhost:8001"
    FRP_PUBLIC_URL: str = ""

    # Rate Limiting
    SMS_RATE_LIMIT_PER_MINUTE: int = 1
    SMS_RATE_LIMIT_PER_HOUR: int = 5
    SMS_RATE_LIMIT_PER_DAY: int = 10

    class Config:
        env_file = ".env"


settings = Settings()