import hashlib
import random
import string
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict
import httpx

from app.config import settings


class WeChatPayService:
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_key = settings.WECHAT_API_KEY
        self.notify_url = settings.WECHAT_NOTIFY_URL
        self.client = httpx.AsyncClient()

    def generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def sign(self, params: Dict) -> str:
        """生成微信支付签名"""
        # Filter empty values and sign
        filtered = {k: v for k, v in params.items() if v and k != "sign"}
        # Sort by key
        sorted_items = sorted(filtered.items())
        # Create string
        string_a = "&".join([f"{k}={v}" for k, v in sorted_items])
        string_sign_temp = f"{string_a}&key={self.api_key}"
        # SHA256 sign
        return hashlib.sha256(string_sign_temp.encode()).hexdigest().upper()

    async def create_order(
        self,
        order_no: str,
        amount: int,  # 分
        description: str,
        openid: str
    ) -> Dict:
        """创建微信支付订单"""
        if not all([self.appid, self.mch_id, self.api_key]):
            raise RuntimeError("WeChat Pay not configured")

        params = {
            "appid": self.appid,
            "mch_id": self.mch_id,
            "nonce_str": self.generate_nonce_str(),
            "body": description,
            "out_trade_no": order_no,
            "total_fee": amount,
            "spbill_create_ip": "127.0.0.1",
            "notify_url": self.notify_url,
            "trade_type": "JSAPI",
            "openid": openid
        }

        params["sign"] = self.sign(params)

        # Convert to XML
        xml = "<xml>"
        for k, v in params.items():
            xml += f"<{k}>{v}</{k}>"
        xml += "</xml>"

        # Call WeChat API
        response = await self.client.post(
            "https://api.mch.weixin.qq.com/pay/unifiedorder",
            content=xml
        )

        # Parse response
        root = ET.fromstring(response.text)
        result = {child.tag: child.text for child in root}

        if result.get("return_code") != "SUCCESS":
            raise RuntimeError(result.get("return_msg", "Unknown error"))

        if result.get("result_code") != "SUCCESS":
            raise RuntimeError(result.get("err_code_des", "Unknown error"))

        # Generate payment params for frontend
        prepay_id = result.get("prepay_id")
        pay_params = {
            "appId": self.appid,
            "timeStamp": str(int(datetime.utcnow().timestamp())),
            "nonceStr": self.generate_nonce_str(),
            "package": f"prepay_id={prepay_id}",
            "signType": "RSA"  # Updated to RSA for WeChat Pay V3
        }

        return {
            "order_no": order_no,
            "prepay_id": prepay_id,
            "pay_params": pay_params
        }

    def verify_notify(self, xml_data: str) -> Optional[Dict]:
        """验证支付回调通知"""
        root = ET.fromstring(xml_data)
        result = {child.tag: child.text for child in root}

        # Verify sign
        received_sign = result.pop("sign", None)
        calculated_sign = self.sign(result)

        if received_sign != calculated_sign:
            return None

        return result


wechat_pay_service = WeChatPayService()