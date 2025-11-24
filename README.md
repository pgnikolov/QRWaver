
<p align="center">
  <img src="app/static/images/branding/logo_wordmark.png" width="300" alt="QRWaver Logo">
</p>

<h1 align="center">QRWaver</h1>
<p align="center">
🟢 Live Demo: <a href="https://qr.appswork.dev" target="_blank"><strong>https://qr.appswork.dev</strong></a>
</p>

<p align="center"><strong>Open‑source QR generator with live preview, optional frames, scan analytics, and a versioned API</strong></p>
<p align="center">
  Create and preview QR codes in real time. Persist finalized QRs to Cloudflare R2. Track scans via short links.
</p>

---

## 🚀 Features (current state)

- Real‑time preview while typing (no persistence)
- Optional frames (SVG) with client‑side composition and high‑res downloads
- Persistence to Cloudflare R2 (SVG/PNG/JPG)
- Short links for scans at `/s/<slug>` with analytics (IP/UA/referrer/UTM; optional geo via IPinfo)
- Dashboard listing + Delete (DB‑only; R2 asset preserved)
- Auth: Email/Password + Google sign‑in (JWT cookies)
- Versioned API v1 for preview, create, list, and stats
- All QR types currently free; soft limit of 5 saved QRs per user

---

## 🧩 Project Structure

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
│  │  ├─ api_routes.py      # /api/v1/ping, /api/v1/version, (legacy generate placeholder)
│  │  ├─ qr_v1_routes.py    # /api/v1/qr/* (preview, create, list, stats, delete)
│  │  ├─ tracking_routes.py # /s/<slug> short redirects + logging
│  │  ├─ auth_routes.py     # Email/Password auth + Google OAuth redirect flow
│  │  ├─ google_auth.py     # Google id_token API flow
│  │  ├─ main_routes.py     # Pages (index, dashboard)
│  │  └─ qr_routes.py       # QR HTML editors (per type)
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ qr_service.py      # Core QR generation + R2 upload
│  │  ├─ analytics_service.py # Scan logging & stats aggregation
│  │  ├─ r2_service.py      # Cloudflare R2 helpers
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
│  │  ├─ auth/login.html
│  │  ├─ auth/register.html
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

The frontend generates live previews by calling a lightweight API that returns an SVG data URI (no persistence). When a user explicitly saves — or clicks Download while logged in — the app persists the QR by rendering the requested format and uploading to Cloudflare R2, creating a `QRCode` row with a short `slug` for tracked scans.

- Rendering: `qrcode` library; SVG via `qrcode.image.svg.SvgPathImage`, PNG/JPG via in-memory rasterization.
- Frames: client‑side composition; frame SVG contains a `<rect id="QR_ZONE">` region to place the QR image.
- Storage: public R2 URL is stored in `QRCode.file_path`.
- Tracking: `/s/<slug>` logs scan details and redirects (URL type) or shows inline landing for non‑URL payloads.

---

## 📡 API (v1)

Base path: `/api/v1`

### POST `/api/v1/generate`

Public preview helper (no auth, no persistence). This is a thin wrapper that returns a data URI image (SVG by default) similar to `/api/v1/qr/preview`. It supports `format`=`svg|png|jpg` and basic `size`.

Request body:

```json
{
  "type": "text|url|wifi|email|phone|vcard|youtube|social",
  "data": "Hello world",
  "settings": { "format": "svg", "size": 512 }
}
```

Response body (example):

```json
{
  "success": true,
  "image": "data:image/svg+xml;base64,....",
  "mime": "image/svg+xml",
  "width": 512,
  "height": 512,
  "rate_limit": { "limit": 60, "remaining": 59, "window": 60 }
}
```

### POST `/api/v1/qr/preview`

Lightweight preview; no auth; no persistence; rate‑limited.

Request body:

```json
{
  "type": "text|url|wifi|email|phone|vcard|youtube|social",
  "data": "Hello world" ,
  "settings": { "size": 512, "color": "#000000" }
}
```

Successful response (example):

```json
{
  "success": true,
  "image": "data:image/svg+xml;base64, ...",
  "mime": "image/svg+xml",
  "width": 512,
  "height": 512,
  "rate_limit": { "limit": 60, "remaining": 59, "window": 60 }
}
```

### POST `/api/v1/qr/create` (auth required)

Persists a QR to R2 and the database; returns the R2 URL, DB id, and a short link.

```json
{
  "type": "url",
  "data": "https://example.com",
  "settings": { "format": "png", "size": 1024 },
  "frame": "none|frame_whole|frame_phone|frame_bag|frame_2parts"
}
```

Response:

```json
{ "success": true, "url": "https://...r2.../file.png", "record_id": 123, "short_url": "https://host/s/AB12cd34" }
```

Notes: All types are free for now; free users can save up to 5 QRs.

### GET `/api/v1/qr`

List the authenticated user’s saved QRs.

### GET `/api/v1/qr/<id>/stats`

Owner‑only; returns totals, daily series, and top breakdowns by country/device/browser/referrer and UTM.

### DELETE `/api/v1/qr/<id>`

Owner‑only; DB‑only delete (R2 asset is preserved); invalidates short link and hides stats.

### Tracking: `GET /s/<slug>`

Logs a scan and then redirects:
- URL type → 302 to target (auto‑prefixes https:// if missing)
- Non‑URL → small inline landing page rendering content

### General API utilities

`GET /api/v1/ping` → `{ "success": true, "status": "ok" }`

`GET /api/v1/version` → `{ "success": true, "version": "1.0.0" }`

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

Tests live in `tests/test_api_v1.py`. The preview smoke test targets `/api/v1/qr/preview`.

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

## ⚠️ Notes & Limits

- All QR types are currently free; a soft limit of 5 saved QRs per user is enforced on create. Delete older items to free a slot.
- Delete removes only the DB record and disables the short link; the original R2 file remains accessible at its direct URL.
- In dev, tables are ensured with `db.create_all()`. If you started with an older SQLite DB, you may need to delete `instance/qrwaver.db` or add migrations.

## ❤️ Credits

Created with passion & caffeine. Logo © QRWaver.
