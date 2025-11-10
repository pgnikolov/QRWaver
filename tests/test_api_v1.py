import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_ping():
    """
    Sends a GET request to the `BASE_URL/ping` endpoint to test its availability.

    This function performs an HTTP GET request to the `/ping` endpoint of the
    server specified by `BASE_URL`. It asserts that the response status code is
    200, and verifies that the JSON response contains the expected success and
    status fields.

    :return: None
    """
    r = requests.get(f"{BASE_URL}/ping")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["status"] == "ok"

def test_version():
    """
    Tests the `/version` endpoint.

    This function sends a GET request to the `/version` endpoint of the API,
    verifies that the status code is 200, and checks the returned JSON
    data for the presence of the "version" key. It also ensures the
    response indicates success.

    :raises AssertionError: If the status code is not 200, if the "version"
                            key is missing from the response data, or if
                            the "success" field in the response is not true.
    :return: None
    """
    r = requests.get(f"{BASE_URL}/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data
    assert data["success"] is True

def test_generate_text_qr():
    """
    Tests the QR code generation endpoint for creating a QR code from a
    plain text payload. The test verifies that the server response is
    successful and checks the validity of the returned details such as
    image content, MIME type, size, and success status.

    :raises AssertionError: If any of the assertions fail during the test.
    """
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
