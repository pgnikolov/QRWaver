
<p align="center">
  <img src="app/static/images/branding/logo_wordmark.png" width="300" alt="QRWaver Logo">
</p>

<h1 align="center">QRWaver</h1>
<p align="center">
🟢 Live Demo: <a href="https://qr.appswork.dev" target="_blank"><strong>https://qr.appswork.dev</strong></a>
</p>

<p align="center"><strong>Open-source QR generator with dynamic styling and a clean REST API</strong></p>
<p align="center">
  Generate QR codes locally (no external QR APIs) with customizable colors, optional frames, and multiple export formats.
</p>

---

## 🚀 Features

- Generate popular QR types: URL, Text, WiFi, Email, Phone, vCard, Social, YouTube
- Export formats: SVG (vector), PNG, JPEG
- Color, background, error-correction level, and border customization
- Simple REST API at `/api/*` with rate limiting and JSON responses
- Frontend pages and assets included (Jinja templates + static files)
- CORS enabled; centralized logging to file and console

---

## 🧩 Project Structure (current)

```
QRWaver/
├─ app/
│  ├─ __init__.py           # Flask app factory, logging, CORS, blueprints
│  ├─ app.py                # (entry point used by some hosts; app factory imports)
│  ├─ config/
│  │  ├─ __init__.py
│  │  └─ settings.py        # Config, log paths
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ api_routes.py      # /api/generate, /api/ping, /api/version
│  │  ├─ main_routes.py     # Site pages
│  │  └─ qr_routes.py       # QR HTML editors
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ qr_service.py      # Core QR generation service
│  │  ├─ rate_limiter.py    # Simple in-memory rate limiter
│  │  └─ qr_types/          # Payload builders per QR type
│  │     ├─ __init__.py
│  │     ├─ email_qr.py
│  │     ├─ phone_qr.py
│  │     ├─ social_qr.py
│  │     ├─ text_qr.py
│  │     ├─ url_qr.py
│  │     ├─ vcard_qr.py
│  │     ├─ wifi_qr.py
│  │     └─ youtube_qr.py
│  ├─ static/
│  │  ├─ css/
│  │  ├─ images/
│  │  │  ├─ branding/
│  │  │  ├─ frames/
│  │  │  ├─ frames_thumbs/
│  │  │  ├─ icons/
│  │  │  └─ logos/
│  │  └─ js/
│  ├─ templates/
│  │  ├─ about.html
│  │  ├─ base.html
│  │  ├─ index.html
│  │  └─ qr_editors/
│  │     ├─ qr_email.html
│  │     ├─ qr_facebook.html
│  │     ├─ qr_instagram.html
│  │     ├─ qr_linkedin.html
│  │     ├─ qr_phone.html
│  │     ├─ qr_text.html
│  │     ├─ qr_tiktok.html
│  │     ├─ qr_twitter.html
│  │     ├─ qr_url.html
│  │     ├─ qr_vcard.html
│  │     ├─ qr_wifi.html
│  │     └─ qr_youtube.html
│  └─ utils/
│     ├─ __init__.py
│     └─ fetch_logos.py
├─ logs/
│  └─ api.log               # Runtime logs (see Logging)
├─ tests/
│  └─ test_api_v1.py
├─ run.py                   # Local dev entry point
├─ requirements.txt
├─ Procfile                 # For platforms like Heroku/Render
├─ LICENSE
└─ README.md
```

---

## ✅ Installation

1) Clone the repo

```bash
git clone https://github.com/yourname/QRWaver.git
cd QRWaver
```

2) Create and activate a virtual env

```bash
python -m venv venv
# Linux & macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3) Install dependencies

```bash
pip install -r requirements.txt
```

4) Run the development server

```bash
python run.py
```

Then open:

```
http://127.0.0.1:5000/
```

---

## 🧠 How It Works

QRWaver renders QR codes using the `qrcode` library.

- SVG: vector output using `qrcode.image.svg.SvgPathImage`
- PNG/JPEG: raster output produced in-memory and base64-encoded

You control rendering via the `settings` object (see API below):

- `format`: `svg` (default) | `png` | `jpeg`
- `color` / `background`: hex colors (e.g., `#000000`, `#FFFFFF`)
- `error_correction`: `L` | `M` | `Q` | `H` (default `H`)
- `size`: image size (used for raster responses)

Note: `vcard` responses are returned as PNG by design for compatibility with common scanners.

---

## 📡 API

Base path: `/api`

### POST `/api/generate`

Request body:

```json
{
  "type": "text",
  "data": "Hello world",
  "settings": {
    "format": "svg",
    "size": 512,
    "color": "#000000",
    "background": "#FFFFFF",
    "error_correction": "H",
    "border": 4
  }
}
```

Successful response (example):

```json
{
  "success": true,
  "image": "data:image/svg+xml;base64, ...",
  "mime": "image/svg+xml",
  "payload": "Hello world",
  "filename": "qrwaver_text_2025-11-16T19-15-00.svg",
  "width": 512,
  "height": 512,
  "rate_limit": { "limit": 60, "remaining": 59, "window": 60 }
}
```

On validation error:

```json
{ "success": false, "errors": { "data": "Payload required." } }
```

Rate limit exceeded: HTTP 429 with headers `X-RateLimit-*` and body:

```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again later.",
  "limit": 60,
  "remaining": 0,
  "window": 60
}
```

### GET `/api/ping`

```json
{ "success": true, "status": "ok" }
```

### GET `/api/version`

```json
{ "success": true, "version": "1.0.0", "build": "backend-clean" }
```

The app root also exposes `/ping` and `/version` for convenience.

---

## ✅ Supported QR Types

These match the payload builders in `app/services/qr_types/*`:

| Type    | Purpose                         |
|---------|---------------------------------|
| url     | Website link                    |
| text    | Plain text                      |
| wifi    | WiFi network (WPA/WEP/open)     |
| email   | mailto: link                    |
| phone   | tel: link                       |
| vcard   | Contact card                    |
| social  | Social profiles deep-links      |
| youtube | YouTube video/channel           |

Easily extendable by adding new builders in `app/services/qr_types/` and mapping them in `QRService.PAYLOAD_BUILDERS`.

---

## 🎨 Frames & Frontend

- Optional SVG frames live in `app/static/images/frames/*.svg`
- Thumbnails in `app/static/images/frames_thumbs/`
- Client-side composition and preview logic lives in `app/static/js/script.js`
- Jinja templates for editors are in `app/templates/qr_editors/*`

If your frame SVG contains a rectangle with id `QR_ZONE`, the client can position the QR image there.

---

## 🖨️ Export Quality

- SVG: pixel-perfect, fully vector
- PNG/JPEG: high-quality raster output; control size via `settings.size`

---

## 🧪 Testing

Run the test suite with pytest:

```bash
pytest
```

Tests live in `tests/test_api_v1.py`.

---

## 📜 Logging

Centralized logging is configured in `app/__init__.py`:

- Console logs (useful for Docker/Render)
- File logs at `logs/api.log`

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes and open a PR
4. All contributions welcome 🎉

---

## 📄 License

MIT — free for personal & commercial use.

---

## ❤️ Credits

Created with passion & caffeine. Logo © QRWaver.
