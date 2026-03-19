import pytest
import sys
from unittest.mock import MagicMock

# Mock oss2 before importing app module to avoid Python 3.12 compatibility issues
sys.modules['oss2'] = MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_voices_unauthorized():
    response = client.get("/api/voices")
    assert response.status_code in [401, 403]

def test_create_voice_unauthorized():
    response = client.post("/api/voices", json={"name": "Test"})
    assert response.status_code in [401, 403]