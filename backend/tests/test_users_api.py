import pytest
import sys
from unittest.mock import MagicMock

# Mock oss2 before importing app module to avoid Python 3.12 compatibility issues
sys.modules['oss2'] = MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_user_info_unauthorized():
    response = client.get("/api/users/me")
    assert response.status_code in [401, 403]

def test_update_user_info_unauthorized():
    response = client.put("/api/users/me", json={"nickname": "Test"})
    assert response.status_code in [401, 403]