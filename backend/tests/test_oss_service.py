import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock oss2 before importing app module to avoid Python 3.12 compatibility issues
sys.modules['oss2'] = MagicMock()

from datetime import datetime
from app.services.oss_service import OSSService


@pytest.fixture
def oss_service():
    with patch('app.services.oss_service.oss2.Auth'):
        with patch('app.services.oss_service.oss2.Bucket'):
            service = OSSService()
            service.bucket = Mock()
            return service


def test_generate_key(oss_service):
    key = oss_service.generate_key("user_123", "voices", "test.wav")
    assert key.startswith("user_123/voices/")
    assert key.endswith(".wav")


def test_generate_upload_url(oss_service):
    oss_service.bucket.sign_url.return_value = "https://oss.example.com/signed-url"

    result = oss_service.generate_upload_url("user_123", "voices", "test.wav")

    assert result["key"].startswith("user_123/voices/")
    assert result["url"] == "https://oss.example.com/signed-url"
    assert result["expires_in"] == 3600


def test_generate_download_url(oss_service):
    oss_service.bucket.sign_url.return_value = "https://oss.example.com/download-url"

    result = oss_service.generate_download_url("user_123/voices/test.wav")

    assert result["url"] == "https://oss.example.com/download-url"
    assert result["expires_in"] == 3600