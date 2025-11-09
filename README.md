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
│   ├── **init**.py
│   ├── config/
│   │   ├── **init**.py
│   │   └── settings.py
│   │
│   ├── routes/
│   │   ├── **init**.py
│   │   ├── main_routes.py         ← home, about, contact
│   │   ├── qr_routes.py           ← all QR type forms + preview
│   │   └── api_routes.py          ← REST API v1
│   │
│   ├── services/
│   │   ├── **init**.py
│   │   ├── qr_service.py          ← handles validation, image gen
│   │   ├── rate_limiter.py        ← per-IP limiter for API/UI
│   │   └── qr_types/              ← individual QR type modules
│   │       ├── **init**.py
│   │       ├── url_qr.py
│   │       ├── vcard_qr.py
│   │       ├── wifi_qr.py
│   │       ├── email_qr.py
│   │       ├── phone_qr.py
│   │       ├── text_qr.py
│   │       ├── social_qr.py
│   │       ├── location_qr.py
│   │       ├── youtube_qr.py
│   │       ├── event_qr.py
│   │       ├── crypto_qr.py
│   │       ├── appstore_qr.py
│   │       └── menu_qr.py
│   │
│   ├── utils/
│   │   ├── **init**.py
│   │   ├── style_utils.py         ← QR rounding, gradients, etc.
│   │   └── url_shortener.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html             ← QR type selector (grid)
│   │   ├── qr_editor.html         ← Main builder page (customization)
│   │   ├── result.html            ← After generation (preview + download)
│   │   └── includes/
│   │       └── modals.html, navbar.html, footer.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   ├── images/
│   │   │   ├── logos/
│   │   │   │   ├── facebook.svg
│   │   │   │   ├── instagram.svg
│   │   │   │   ├── linkedin.svg
│   │   │   │   ├── youtube.svg
│   │   │   │   ├── tiktok.svg
│   │   │   │   ├── twitter.svg
│   │   │   │   ├── appstore.svg
│   │   │   │   ├── googleplay.svg
│   │   │   │   ├── crypto.svg
│   │   │   │   └── restaurant.svg
│   │   │   ├── icons/
│   │   │   │   ├── qr.svg
│   │   │   │   ├── wifi.svg
│   │   │   │   ├── event.svg
│   │   │   │   ├── vcard.svg
│   │   │   │   └── location.svg
│   │   │   └── av/
│   │   │       ├── logo_light.svg
│   │   │       └── logo_dark.svg
│   │
│   └── app.py  ← entry point for Flask (create_app)
│
├── requirements.txt
├── run.py       ← flask run entry
├── README.md
└── .env

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
python test_api.py
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
