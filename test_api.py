import requests
import json
import time

API_URL = "http://127.0.0.1:5000/api/generate"


def test(payload, delay=1.2):
    """Send one test payload and print a readable summary."""
    qr_type = payload.get("type", "unknown")
    print(f"\n🔹 Testing {qr_type.upper()} QR...")

    try:
        r = requests.post(API_URL, json=payload, timeout=10)
        print("Status:", r.status_code)

        # Try decode JSON
        try:
            data = r.json()
            if r.status_code == 200 and data.get("success"):
                print(f"✅ OK → Keys: {list(data.keys())}")
                print(f"   Payload: {data.get('payload')[:80]}{'...' if len(data.get('payload')) > 80 else ''}")
            elif r.status_code == 429:
                print("⚠️ Rate limit hit → waiting 3s before next test...")
                time.sleep(3)
            else:
                print("❌ API Error:", data)
        except json.JSONDecodeError:
            print("❌ Failed to decode JSON")
            print("Response text (first 300 chars):")
            print(r.text[:300])

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

    time.sleep(delay)


# --- TEST PAYLOADS ---
tests = [
    # 1️⃣ URL
    {
        "type": "url",
        "data": "https://qrwaver.app",
        "settings": {"size": 300, "color": "#000000"},
    },

    # 2️⃣ TEXT
    {
        "type": "text",
        "data": "Hello from QRWeaver!",
        "settings": {"size": 300, "color": "#2563EB"},
    },

    # 3️⃣ WIFI
    {
        "type": "wifi",
        "data": {
            "ssid": "MyNetwork",
            "password": "supersecret",
            "encryption": "WPA2",
            "hidden": False,
        },
        "settings": {"size": 300, "color": "#111827"},
    },

    # 4️⃣ EMAIL
    {
        "type": "email",
        "data": {
            "to": "hello@qrwaver.app",
            "subject": "QRWeaver test",
            "body": "It works perfectly!",
        },
        "settings": {"size": 300, "color": "#4B5563"},
    },

    # 5️⃣ PHONE
    {
        "type": "phone",
        "data": "+359888123456",
        "settings": {"size": 300, "color": "#16A34A"},
    },

    # 6️⃣ VCARD
    {
        "type": "vcard",
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+123456789",
            "email": "john@doe.com",
            "company": "QRWeaver",
            "title": "Developer",
        },
        "settings": {"size": 300, "color": "#7C3AED"},
    },

    # 7️⃣ LOCATION
    {
        "type": "location",
        "data": {"lat": 42.6977, "lng": 23.3219},
        "settings": {"size": 300, "color": "#DC2626"},
    },

    # 8️⃣ YOUTUBE
    {
        "type": "youtube",
        "data": "https://youtu.be/dQw4w9WgXcQ",
        "settings": {"size": 300, "color": "#EAB308"},
    },

    # 9️⃣ EVENT
    {
        "type": "event",
        "data": {
            "summary": "Team Meeting",
            "location": "Office 204",
            "start": "2025-11-10T10:00:00",
            "end": "2025-11-10T11:00:00",
        },
        "settings": {"size": 300, "color": "#0891B2"},
    },

    # 🔟 CRYPTO
    {
        "type": "crypto",
        "data": {
            "currency": "BTC",
            "address": "1BitcoinAddress123",
            "amount": "0.01",
        },
        "settings": {"size": 300, "color": "#F97316"},
    },

    # 11️⃣ APPSTORE
    {
        "type": "appstore",
        "data": {"url": "https://apps.apple.com/app/id123456"},
        "settings": {"size": 300, "color": "#0EA5E9"},
    },

    # 12️⃣ MENU
    {
        "type": "menu",
        "data": "https://qrwaver.app/menu/restaurant123",
        "settings": {"size": 300, "color": "#D946EF"},
    },

    # 13️⃣ SOCIAL
    {
        "type": "social",
        "data": {"platform": "instagram", "username": "qrwaver"},
        "settings": {"size": 300, "color": "#EC4899"},
    },
]


if __name__ == "__main__":
    print("🚀 Starting API tests...\n")
    for t in tests:
        test(t)
    print("\n✅ All tests completed.\n")
