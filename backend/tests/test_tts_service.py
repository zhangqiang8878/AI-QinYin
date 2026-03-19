import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from app.services.tts_service import TTSService

@pytest.fixture
def tts_service():
    return TTSService()

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_clone_voice(mock_post, tts_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "voice_id": "voice_abc123",
            "duration": 10.5
        }
    }
    mock_post.return_value = mock_response

    result = await tts_service.clone_voice(
        audio_url="https://example.com/audio.wav",
        voice_name="Test Voice"
    )

    assert result["voice_id"] == "voice_abc123"
    assert result["duration"] == 10.5

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_synthesize(mock_post, tts_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "audio_url": "https://example.com/output.wav",
            "duration": 180.0
        }
    }
    mock_post.return_value = mock_response

    result = await tts_service.synthesize(
        voice_id="voice_abc123",
        text="Hello world",
        speed=1.0
    )

    assert result["audio_url"] == "https://example.com/output.wav"
    assert result["duration"] == 180.0