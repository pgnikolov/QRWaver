
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
- Short links for scans at `/s/<slug>` with analytics
  - Totals and daily series
  - Unique scans by IP (all‑time) and per‑day unique series
  - Breakdowns by country, device type, browser
  - UTM attribution (source/medium/campaign/term/content)
  - Optional geo enrichment via IPinfo when `IPINFO_TOKEN` is set
- Dashboard listing + Delete (DB‑only; R2 asset preserved)
- Auth: Email/Password + Google sign‑in (JWT cookies)
- Versioned API v1 for preview, create, list, and stats
- All QR types currently free; soft limit of 5 saved QRs per user

- Campaign tagging (UTM) at creation time
  - Set UTMs when creating a QR (URL, text, email, phone, vCard, Facebook, Instagram, LinkedIn, Twitter/X, TikTok, YouTube)
  - Stored as defaults on the QR; used for analytics if a scan arrives without explicit UTMs
  - For URL QRs, UTMs are forwarded to the destination URL (without overwriting UTMs that are already present there)
  - UTM stats exclude empty/unspecified values; only user‑provided labels appear in the breakdowns

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

The frontend generates live previews by calling a lightweight API that returns an SVG data URI (no persistence). When a user explicitly saves — or clicks Download while logged in — the app persists the QR by rendering the requested format and uploading to Cloudflare R2. A `QRCode` row is created together with a short `slug` for tracked scans, and the actual QR image encodes the short URL so every real‑world scan passes through `/s/<slug>` and gets counted.

- Rendering: `qrcode` library; SVG via `qrcode.image.svg.SvgPathImage`, PNG/JPG via in-memory rasterization.
- Frames: client‑side composition; frame SVG contains a `<rect id="QR_ZONE">` region to place the QR image.
- Storage: public R2 URL is stored in `QRCode.file_path`.
- Tracking: `/s/<slug>` logs scan details and redirects (URL type) or shows inline landing for non‑URL payloads.
  - Base URL for short links
    - Development: uses the current request host (e.g., http://127.0.0.1:5000) so local slugs resolve correctly.
    - Production: uses `PUBLIC_BASE_URL` when set; otherwise falls back to the request host.
  - UTM defaults stored on each `QRCode` are merged with incoming query UTMs (incoming takes precedence). The merged UTMs are logged with the scan, and for URL QRs they are forwarded to the destination URL without overwriting any `utm_*` already present there. In analytics, empty or unspecified UTM values are excluded from breakdowns (only labeled values are shown).
  - Unique counts: besides total scans, analytics compute unique visitors by IP in two ways:
    - All‑time unique by IP (within the requested time window)
    - Daily unique by IP series (distinct IPs per calendar day)

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
  "frame": "none|frame_whole|frame_phone|frame_bag|frame_2parts",
  "utm": {
    "utm_source": "instagram",
    "utm_medium": "social",
    "utm_campaign": "winter_2025",
    "utm_term": "",
    "utm_content": "v1_blue"
  }
}
```

Response:

```json
{ "success": true, "url": "https://...r2.../file.png", "record_id": 123, "short_url": "https://host/s/AB12cd34" }
```

Notes:
- UTMs can be provided either inside a top‑level `utm` object (preferred) or as flat fields (`utm_source`, `utm_medium`, ...). Empty values are ignored.
- Defaults are stored on the QR and used for analytics if a scan arrives without explicit UTMs. For URL QRs, the merged UTMs are added to the destination URL on redirect without overwriting any existing `utm_*` already present there.
- All types are free for now; free users can save up to 5 QRs.

### GET `/api/v1/qr`

List the authenticated user’s saved QRs.

### GET `/api/v1/qr/<id>/stats`

Owner‑only; returns totals, unique counts, daily series (and daily unique), plus top breakdowns by country, device type, browser, and UTM.

Response shape (fields of interest):

```
{
  "success": true,
  "totals": { "scans": 42 },
  "uniques": { "all_time": 27 },           // distinct IPs in range
  "series": [ { "date": "2025-12-02", "count": 5 }, ... ],
  "series_unique": [ { "date": "2025-12-02", "count": 4 }, ... ],
  "by_country": [ { "country": "DE", "count": 12 }, ... ],
  "by_device": [ { "device_type": "mobile", "count": 20 }, ... ],
  "by_browser": [ { "browser": "Chrome", "count": 18 }, ... ],
  "utm": {
    "utm_source": [ { "utm_source": "flyer", "count": 7 }, ... ],
    "utm_medium": [ ... ],
    "utm_campaign": [ ... ],
    "utm_term": [ ... ],
    "utm_content": [ ... ]
  }
}
```

Notes:
- UTM lists exclude empty/unspecified values (we don’t show an `(unknown)` bucket for UTMs).
- Uniques are IP‑based by design (simple, fast). See Design Decisions for trade‑offs.

### DELETE `/api/v1/qr/<id>`

Owner‑only; DB‑only delete (R2 asset is preserved); invalidates short link and hides stats.

### Tracking: `GET /s/<slug>`

Logs a scan and then redirects or renders inline:
- URL type → 302 to target (auto‑prefixes https:// if missing). Before redirecting, the service merges allowed `utm_*` from the short link with the QR’s stored defaults (incoming query values win) and forwards the result to the destination URL without overwriting any UTMs already present on the target URL.
- Non‑URL → small inline landing page rendering content. Scans are still logged with geo/device/browser and UTM attribution (using incoming or stored defaults).

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

UTM at creation time is supported in the editors for: URL, Text, Email, Phone, vCard, Facebook, Instagram, LinkedIn, Twitter/X, TikTok, YouTube. UTMs are not editable after creation.

---

## 🎨 Frames & Frontend

- Optional SVG frames live in `app/static/images/frames/*.svg`
- Thumbnails in `app/static/images/frames_thumbs/`
- Client-side composition and preview logic lives in `app/static/js/script.js`
- Jinja templates for editors are in `app/templates/qr_editors/*`

- Each editor that supports UTMs shows a small info button next to “Campaign (optional)”. It toggles an inline help box explaining the five UTM fields. This toggle is implemented inline (no dependency on a specific JS version), so it works even under aggressive static caching.

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

---

## 🧭 Design decisions and trade‑offs (with references)

This section explains specific choices in the codebase and why they were preferred over common alternatives. Paths and symbols below refer to this repository.

- App factory: `app.__init__.py:create_app`
  - Chosen over the simpler `app.app:create_app` as the default entry point because it centralizes extensions, logging, CORS, blueprints, and error handlers in one place. The "simple" factory remains for hosts expecting a minimal app object, but the main app uses the richer factory.

- JWT in cookies, not Authorization headers
  - See `app/config/settings.py` → `Config.JWT_TOKEN_LOCATION = ["cookies"]` and related flags. Cookies reduce friction for the browser client and avoid leaking tokens to third‑party scripts via `Authorization` headers. In production the config switches `JWT_COOKIE_SECURE = True`. We intentionally disabled CSRF here for simplicity (`JWT_COOKIE_CSRF_PROTECT = False`) — acceptable for this demo; enable it for a hardened deployment.

- Rate limiting: in‑memory `SimpleRateLimiter` instead of Redis
  - Used in `app/routes/api_routes.py` and `app/routes/qr_v1_routes.py`. The in‑process limiter keeps the preview endpoints self‑contained and fast to run locally. For multi‑instance deployments use Redis or another external store; the interface in `app/services/rate_limiter.py` is written so a drop‑in backend can replace it.

- Cloudflare R2 via `boto3` S3 client, not vendor‑specific SDK
  - See `app/services/r2_service.py`. R2 implements the S3 API, so `boto3.client("s3", endpoint_url=R2_ENDPOINT_URL, ...)` keeps the code portable and easy to swap for AWS S3, MinIO, or LocalStack. Two thin helpers are exposed: `upload_svg(...)` and `upload_image(...)` to make MIME types explicit and avoid mistakes.

- SVG engine: `qrcode.image.svg.SvgPathImage` rather than basic raster only
  - In `app/services/qr_service.py` `_generate_svg_bytes` uses `SvgPathImage`. Vector output scales cleanly and drives the live preview as a data URI. PNG/JPG paths exist for downloads, but SVG stays the default for previews because it is small and crisp at any size. Error correction is set to `qrcode.constants.ERROR_CORRECT_H` to tolerate frame overlays and minor print defects.

- Short links redirect only for URL payloads
  - In `app/routes/tracking_routes.py`, non‑URL QR types render a minimal landing page that shows the payload instead of redirecting. This avoids constructing unsafe or invalid redirects for content like Wi‑Fi configs or vCards, while still logging the scan.

- Keep R2 files on delete (DB‑only removal)
  - `DELETE /api/v1/qr/<id>` removes the DB record but leaves the asset in R2. This is deliberate: it avoids destructive storage operations and allows later retention/cleanup policies to run out‑of‑band.

- Source of truth for base URLs
  - `PUBLIC_BASE_URL` in `app/config/settings.py` is optional. If set, short links use it as the prefix; otherwise the app falls back to the incoming request host. This helps when serving behind a proxy or CDN with a public hostname.

- Minimal UA parsing, no heavy user‑agent libraries
  - `app/services/analytics_service.py` uses straightforward string checks in `_detect_device` for device/OS/browser and optional `ipinfo.io` lookup for geo. This avoids adding large parsers and keeps latency low. If you need tighter attribution fidelity, this class is the place to extend.

- Unique scans counted by IP (all‑time and per‑day)
  - We expose two "unique" metrics calculated at query time in `AnalyticsService.get_stats()`: a single all‑time distinct IP count (within the requested window) and a daily series of distinct IPs. This keeps storage simple (no extra indices/tables) and works well for lightweight attribution.
  - Why IP and not IP+UA or cookies: IP‑only is fast and stable server‑side; UA often collapses on scanners and cookies don’t exist for native camera apps. If you need stricter uniqueness, extend `get_stats()` to use `(ip, ua)` or add a hashing strategy.
  - Limitations: NAT/VPNs can under/over‑count. We accept that trade‑off for speed and zero client requirements.

- Two API namespaces for compatibility
  - `app/routes/api_routes.py` is a compact legacy generator mounted at `/api/v1/generate` in the main factory (`app.__init__.py`). The versioned API lives in `app/routes/qr_v1_routes.py` under `/api/v1/qr/*`. Keeping both allows incremental migration for clients.

---

## 🔐 Environment and secrets

- Configuration comes from `.env` loaded in `app/config/settings.py` (`dotenv`). Do not commit real secrets. Rotate any leaked keys immediately.
- Required keys for storage and auth:
  - `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, `R2_PUBLIC_BASE_URL`
  - `SECRET_KEY`, `JWT_SECRET_KEY`
  - Optional: `PUBLIC_BASE_URL` for short links, Google OAuth keys, SMTP settings, `IPINFO_TOKEN` for geo.

### Geo enrichment (`IPINFO_TOKEN`)
- Purpose: enrich scan logs with `country/region/city` by calling `https://ipinfo.io/<ip>?token=...` in `AnalyticsService`.
- Get a token:
  1) Sign up at https://ipinfo.io/signup
  2) Copy the value from https://ipinfo.io/account/token
- Configure:
  - Local: add to `.env`
    ```
    IPINFO_TOKEN=your_real_token_here
    ```
  - Production: set as an environment variable in your hosting panel.
- Verify quickly:
  ```
  curl "https://ipinfo.io/8.8.8.8?token=YOUR_REAL_TOKEN"
  ```
  You should see JSON containing `country`, `region`, `city`, and `loc` (parsed to `lat`/`lon`).
- Notes: ensure outbound HTTPS to `ipinfo.io` is allowed and that your proxy forwards client IP via `CF-Connecting-IP`, `X-Real-IP`, or `X-Forwarded-For`; otherwise geo will reflect the proxy or be empty. Free plan limits apply.

---

## 🛠️ Local development tips

- Use the provided `run.py` for local runs; it imports the main factory and starts the server with sane defaults.
- Logs are written to `logs/api.log` as configured in `app/config/settings.py` and set up by `app.__init__.py`.
- If you run multiple instances (e.g., gunicorn workers) and rely on rate limits, switch the limiter to a shared backend.

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

## PostgreSQL (Supabase) migration — Why and How

This project has been upgraded from SQLite to PostgreSQL (via Supabase). Below is a concise guide explaining the reasons, the exact changes made, and how to run everything locally and in production.

### Why switch from SQLite to PostgreSQL?
- Reliability at scale: PostgreSQL supports concurrent writes, robust transactions, and stricter typing.
- Cloud‑hosted DB (Supabase): managed backups, metrics, and network access; no local Postgres required.
- Better SQL features: powerful indexes, JSON/aggregations, and extensions if needed later.

### What changed in the codebase
1) Driver and connection URL
   - We use the modern psycopg v3 driver.
   - `.env` uses a URL like:
     ```
     DATABASE_URL=postgresql+psycopg://<user>:<pass>@db.<project>.supabase.co:5432/postgres?sslmode=require
     ```
   - `requirements.txt` includes:
     ```
     psycopg[binary]
     ```

2) Alembic migrations as the source of truth
   - Migrations are linear and applied to Postgres with `flask db upgrade`.
   - We fixed a boolean default to be PostgreSQL‑safe (`sa.true()`), and added a dedicated migration to create useful indexes.
   - We also resolved a previous “multiple heads” situation by linearizing the chain.

3) Safe app initialization (no auto‑DDL on Postgres)
   - `app/__init__.py` will call `db.create_all()` only when the dialect is SQLite.
   - On Postgres we rely solely on Alembic, preventing accidental DuplicateTable errors and drift.

4) Connection stability for cloud DBs
   - `app/config/settings.py` adds `SQLALCHEMY_ENGINE_OPTIONS`:
     ```python
     SQLALCHEMY_ENGINE_OPTIONS = {
       "pool_pre_ping": True,
       "pool_recycle": 1800,
     }
     ```
     This reduces errors from stale connections in managed environments.

5) Config hardening
   - We removed the default SQLite fallback from base `Config`. Only `DevelopmentConfig` keeps the SQLite fallback.
   - `ProductionConfig` fails fast if `DATABASE_URL` isn’t set, to avoid silent misconfigurations.

6) Procfile for production web server
   - Uses Gunicorn with sensible defaults:
     ```
     web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --preload --log-file -
     ```

### Advantages of these choices
- Fewer surprises: No implicit `create_all()` on Postgres; schema changes live in Alembic.
- Better performance and query plans thanks to explicit indexes.
- More robust connections in serverless/managed environments.
- Safer deployments: production won’t silently fall back to a local SQLite file.

### One‑time migration checklist (Postgres/Supabase)
1) Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```
2) Provide the Supabase URL in `.env`
   ```
   DATABASE_URL=postgresql+psycopg://<user>:<pass>@db.<project>.supabase.co:5432/postgres?sslmode=require
   ```
3) Apply migrations
   ```powershell
   $env:FLASK_APP="run.py"
   flask db upgrade
   ```
4) Verify connectivity
   ```powershell
   flask shell
   >>> from app.extensions.extensions import db
   >>> db.session.execute(db.text("SELECT 1")).scalar()
   1
   ```
5) Start the app
   ```powershell
   python .\run.py
   ```
   Visit `http://127.0.0.1:5000/ping` — expect `{ success: true }`.

### Cleaning up the old SQLite file
- If you no longer need legacy local data, remove only the file (keep the `instance/` folder):
  ```powershell
  if (Test-Path .\instance\qrwaver.db) { Remove-Item .\instance\qrwaver.db }
  ```

### Common pitfalls and fixes
- DuplicateTable on first `flask db upgrade`:
  - Cause: tables were created earlier by `create_all()` before we disabled it for Postgres.
  - Fix: drop the stray tables (or the `public` schema if empty), then re‑run `flask db upgrade`.

- “Multiple heads” in Alembic:
  - We resolved this by setting a clear linear chain:
    `423c21b1ff06 -> 7b2c3df0a9d3 -> c8b9e2a1f3c4 -> 9f3a1c2dadd -> d1e2f3a4b5c6`.

- Duplicate index errors:
  - Index migration now checks for existing indexes before creating them, so it’s idempotent across environments.

### Environment variables (partial list)
- Database
  - `DATABASE_URL` — required in staging/production. Use `?sslmode=require` for Supabase.
- Secrets
  - `SECRET_KEY`, `JWT_SECRET_KEY` — provide non‑default values in production.
- Cloudflare R2 (file/CDN)
  - `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, `R2_PUBLIC_BASE_URL`
- OAuth and Email
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
  - `MAIL_*` (server/port/username/password/TLS/SSL)

### Security notes
- Do not commit real `.env` credentials to version control.
- Rotate any secrets that have been exposed during development.
- Consider enabling CSRF protection for JWT cookies in production if your frontend uses them for state‑changing requests.

### Testing
```
pytest -q
```
The suite includes a smoke test for `POST /api/generate` (quick SVG data‑URI preview), and health/version checks.
