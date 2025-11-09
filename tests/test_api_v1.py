import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_ping():
    r = requests.get(f"{BASE_URL}/ping")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["status"] == "ok"

def test_version():
    r = requests.get(f"{BASE_URL}/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data
    assert data["success"] is True

def test_generate_text_qr():
    payload = {
        "type": "text",
        "data": "Hello from automated test!",
        "settings": {"size": 300, "color": "#2563EB"}
    }
    r = requests.post(f"{BASE_URL}/api/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "image" in data
    assert data["mime"] == "image/png"
    assert data["width"] == 300
