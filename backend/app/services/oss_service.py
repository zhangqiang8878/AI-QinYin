import oss2
import uuid
from datetime import datetime
from typing import Optional

from app.config import settings


class OSSService:
    def __init__(self):
        self.auth = None
        self.bucket = None

        if settings.OSS_ACCESS_KEY_ID and settings.OSS_ACCESS_KEY_SECRET:
            self.auth = oss2.Auth(
                settings.OSS_ACCESS_KEY_ID,
                settings.OSS_ACCESS_KEY_SECRET
            )
            self.bucket = oss2.Bucket(
                self.auth,
                f"https://{settings.OSS_ENDPOINT}",
                settings.OSS_BUCKET_NAME
            )

    def generate_key(self, user_id: str, folder: str, filename: str) -> str:
        """生成OSS对象键"""
        ext = filename.split('.')[-1] if '.' in filename else 'wav'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        return f"{user_id}/{folder}/{timestamp}_{unique_id}.{ext}"

    def generate_upload_url(
        self,
        user_id: str,
        folder: str,
        filename: str,
        expire: int = 3600
    ) -> dict:
        """生成上传URL"""
        if not self.bucket:
            raise RuntimeError("OSS not configured")

        key = self.generate_key(user_id, folder, filename)
        url = self.bucket.sign_url('PUT', key, expire, headers={'Content-Type': 'application/octet-stream'})

        return {
            "key": key,
            "url": url,
            "expires_in": expire,
            "public_url": f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{key}"
        }

    def generate_download_url(self, key: str, expire: int = 3600) -> dict:
        """生成下载URL"""
        if not self.bucket:
            raise RuntimeError("OSS not configured")

        url = self.bucket.sign_url('GET', key, expire)
        return {
            "url": url,
            "expires_in": expire
        }

oss_service = OSSService()