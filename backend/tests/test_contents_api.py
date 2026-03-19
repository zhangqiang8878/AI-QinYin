import pytest
import sys
from unittest.mock import MagicMock

sys.modules['oss2'] = MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_contents_unauthorized():
    response = client.get("/api/contents")
    assert response.status_code in [401, 403]

def test_create_content_unauthorized():
    response = client.post("/api/contents", json={
        "type": "story",
        "voice_id": "test_voice"
    })
    assert response.status_code in [401, 403]

def test_get_content_unauthorized():
    response = client.get("/api/contents/test_id")
    assert response.status_code in [401, 403]