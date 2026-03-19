import httpx
from typing import Optional
from app.config import settings

class TTSService:
    def __init__(self):
        self.base_url = settings.TTS_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout for synthesis

    async def clone_voice(self, audio_url: str, voice_name: Optional[str] = None) -> dict:
        """克隆音色"""
        response = await self.client.post(
            f"{self.base_url}/clone",
            json={
                "audio_url": audio_url,
                "voice_name": voice_name or "Custom Voice"
            }
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            raise RuntimeError(data.get("message", "Voice cloning failed"))

        return data["data"]

    async def synthesize(
        self,
        voice_id: str,
        text: str,
        speed: float = 1.0,
        pitch: float = 0.0
    ) -> dict:
        """合成语音"""
        response = await self.client.post(
            f"{self.base_url}/synthesize",
            json={
                "voice_id": voice_id,
                "text": text,
                "speed": speed,
                "pitch": pitch
            }
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            raise RuntimeError(data.get("message", "Synthesis failed"))

        return data["data"]

    async def health_check(self) -> bool:
        """检查TTS服务健康状态"""
        try:
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False

tts_service = TTSService()