import pytest
from unittest.mock import Mock, patch
from app.services.sms_service import SMSService, SMSResult


@pytest.fixture
def sms_service():
    return SMSService()


def test_generate_code():
    service = SMSService()
    code = service.generate_code()
    assert len(code) == 6
    assert code.isdigit()


@patch('app.services.sms_service.redis_client')
def test_check_rate_limit_allowed(mock_redis):
    mock_redis.get.return_value = None
    mock_redis.pipeline.return_value = Mock(
        setex=Mock(return_value=None),
        incr=Mock(return_value=None),
        expire=Mock(return_value=None),
        execute=Mock(return_value=None)
    )

    service = SMSService()
    result = service.check_rate_limit("13800138000")
    assert result is True


@patch('app.services.sms_service.redis_client')
def test_check_rate_limit_denied(mock_redis):
    mock_redis.get.return_value = "1"  # Already sent within minute

    service = SMSService()
    result = service.check_rate_limit("13800138000")
    assert result is False