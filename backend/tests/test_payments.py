import pytest
from unittest.mock import Mock, patch
from app.services.wechat_pay import WeChatPayService


@pytest.fixture
def pay_service():
    return WeChatPayService()


def test_generate_nonce_str(pay_service):
    nonce = pay_service.generate_nonce_str()
    assert len(nonce) == 32


def test_sign(pay_service):
    params = {
        "appid": "test_appid",
        "mch_id": "test_mch_id",
        "nonce_str": "test_nonce"
    }
    sign = pay_service.sign(params)
    assert isinstance(sign, str)
    assert len(sign) > 0