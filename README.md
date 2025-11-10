# QRWeaver (v2.0)

Modernized and modular QR code generator — now fully API-driven and ready for frontend integration.

---

## ⚙️ Overview

The QRWeaver project has undergone a **major refactor**.  
The backend was rewritten into a **modular Flask architecture** with clear separation of concerns.

This version introduces:
- Unified API endpoint (`/api/generate`)
- Dedicated service layer for QR logic
- Extensible QR type system (`app/services/qr_types/`)
- Clean file structure with templates, static assets, and utilities
- Built-in rate limiting and payload validation
- Automatic `filename` and base64 image generation

---

## 🧩 New Project Structure

```

QRWaver/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api_routes.py
│   │   ├── main_routes.py
│   │   └── qr_routes.py
│   ├── services/
│   │   ├── qr_types/
│   │   │   ├── __init__.py
│   │   │   ├── appstore_qr.py
│   │   │   ├── crypto_qr.py
│   │   │   ├── email_qr.py
│   │   │   ├── event_qr.py
│   │   │   ├── location_qr.py
│   │   │   ├── menu_qr.py
│   │   │   ├── phone_qr.py
│   │   │   ├── social_qr.py
│   │   │   ├── text_qr.py
│   │   │   ├── url_qr.py
│   │   │   ├── vcard_qr.py
│   │   │   ├── wifi_qr.py
│   │   │   └── youtube_qr.py
│   │   ├── __init__.py
│   │   ├── qr_service.py
│   │   └── rate_limiter.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── images/
│   │   │   ├── branding/
│   │   │   │   └── logo_wordmark.png
│   │   │   ├── frames/
│   │   │   │   ├── frame_2parts.svg
│   │   │   │   ├── frame_bag.svg
│   │   │   │   ├── frame_phone.svg
│   │   │   │   └── frame_whole.svg
│   │   │   ├── frames_thumbs/
│   │   │   │   ├── bag_96.png
│   │   │   │   ├── phone_96.png
│   │   │   │   ├── rounded_96.png
│   │   │   │   └── two_parts_96.png
│   │   │   ├── icons/
│   │   │   │   ├── appstore.svg
│   │   │   │   ├── bitcoin.svg
│   │   │   │   ├── crypto.svg
│   │   │   │   ├── email.svg
│   │   │   │   ├── event.svg
│   │   │   │   ├── facebook.svg
│   │   │   │   ├── googleplay.svg
│   │   │   │   ├── instagram.svg
│   │   │   │   ├── linkedin.svg
│   │   │   │   ├── location.svg
│   │   │   │   ├── phone.svg
│   │   │   │   ├── qr.svg
│   │   │   │   ├── restaurant.svg
│   │   │   │   ├── text.svg
│   │   │   │   ├── tiktok.svg
│   │   │   │   ├── twitter.svg
│   │   │   │   ├── vcard.svg
│   │   │   │   ├── wifi.svg
│   │   │   │   └── youtube.svg
│   │   │   ├── logos/
│   │   │       ├── appstore.svg
│   │   │       ├── bitcoin.svg
│   │   │       ├── crypto.svg
│   │   │       ├── facebook.svg
│   │   │       ├── googleplay.svg
│   │   │       ├── instagram.svg
│   │   │       ├── linkedin.svg
│   │   │       ├── restaurant.svg
│   │   │       ├── tiktok.svg
│   │   │       ├── x.svg
│   │   │       └── youtube.svg
│   │   ├── js/
│   │       └── script.js
│   ├── templates/
│   │   ├── includes/
│   │   │   ├── footer.html
│   │   │   ├── modals.html
│   │   │   └── navbar.html
│   │   ├── qr_editors/
│   │   │   ├── qr_appstore.html
│   │   │   ├── qr_crypto.html
│   │   │   ├── qr_email.html
│   │   │   ├── qr_event.html
│   │   │   ├── qr_facebook.html
│   │   │   ├── qr_googleplay.html
│   │   │   ├── qr_instagram.html
│   │   │   ├── qr_linkedin.html
│   │   │   ├── qr_location.html
│   │   │   ├── qr_menu.html
│   │   │   ├── qr_phone.html
│   │   │   ├── qr_text.html
│   │   │   ├── qr_tiktok.html
│   │   │   ├── qr_twitter.html
│   │   │   ├── qr_url.html
│   │   │   ├── qr_vcard.html
│   │   │   ├── qr_wifi.html
│   │   │   └── qr_youtube.html
│   │   ├── about.html
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── qr_editor_placeholder.html
│   │   └── result.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── fetch_logos.py
│   │   ├── style_utils.py
│   │   └── url_shortener.py
│   ├── __init__.py
│   └── app.py
├── logs/
├── tests/
│   └── test_api_v1.py
├── LICENSE
├── README.md
├── requirements.txt
└── run.py


````

---

## 🧠 Architecture Overview

| Layer | Description |
|-------|--------------|
| **routes/** | Handles all web and API routes |
| **services/** | Core business logic (QR generation, validation, limits) |
| **qr_types/** | One module per QR type (e.g., `wifi_qr.py`) |
| **utils/** | Visual helpers (rounded corners, gradients, etc.) |
| **templates/** | HTML templates (Jinja2) for UI |
| **static/** | JS, CSS, and assets for the web interface |

---

## 🌐 API Endpoint

**`POST /api/generate`**

Request example:
```json
{
  "type": "wifi",
  "data": {
    "ssid": "MyNetwork",
    "password": "supersecret",
    "encryption": "WPA2"
  },
  "settings": {
    "size": 400,
    "color": "#000000",
    "rounded_corners": true
  }
}
````

Response:

```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "payload": "WIFI:T:WPA2;S:MyNetwork;P:supersecret;H:false;;",
  "mime": "image/png",
  "width": 400,
  "height": 400,
  "filename": "qrweaver_wifi_2025-11-09T02-00-00.png",
  "rate_limit": {"limit": 3, "remaining": 2}
}
```

---

## 🧪 Local Testing

A full API test runner is included:

```bash
python test_api_legacy.py
```

It runs through all supported QR types and prints live API responses.

---

## 🪄 Next Step: Frontend Integration

The backend is **100% ready**.
Next up — frontend integration using HTML/JS or a React/Vite setup.

Planned:

* QR builder UI (form per type)
* Live preview (base64 image)
* “Download” button using `filename` from API response
* Option to add overlay logo and rounded corners

---

## 🧰 Tech Stack

* Python 3.10+
* Flask 3.x
* Pillow + qrcode
* Flask-CORS
* Dataclasses + PEP8-compliant structure

---

## 🧾 License

MIT © 2025 — QRWeaver Project
