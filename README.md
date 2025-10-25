# QRWaver

Create beautiful, branded QR codes for your social media profiles (Facebook, Instagram, LinkedIn) via a simple web UI or a lightweight HTTP API.

The UI text is currently in Bulgarian, but the app and API are easy to use regardless of language.


## Features
- Branded QR codes per platform with appropriate colors and logo
- Optional shortlinks (compact, human‑friendly profile links)
- Rounded corners option with adjustable radius
- Adjustable QR size
- Download as PNG from the UI
- Simple JSON API returning a base64 PNG data URL


## Demo routes (local)
After starting the server, open:
- Home: http://127.0.0.1:5000/
- Facebook QR page: http://127.0.0.1:5000/social/facebook
- Instagram QR page: http://127.0.0.1:5000/social/instagram
- LinkedIn QR page: http://127.0.0.1:5000/social/linkedin


## Project structure
```
C:/Users/pgnik/PycharmProjects/QRWaver
├─ app.py                       # Entry point for local run
├─ requirements.txt
├─ app/
│  ├─ __init__.py               # Flask app factory and blueprint registration
│  ├─ routes.py                 # Web routes + API endpoint
│  ├─ services/
│  │  └─ qr_service.py          # (service layer, if used)
│  └─ utils/
│     ├─ qr_generator.py        # (placeholder)
│     ├─ social_qr.py           # Main QR generation logic per platform
│     ├─ style_utils.py         # Styling helpers
│     └─ url_shortener.py       # Shortlink builder utilities
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  └─ social/
│     ├─ facebook.html
│     ├─ instagram.html
│     └─ linkedin.html
├─ static/
│  ├─ css/style.css
│  ├─ js/script.js
│  └─ images/logos/
│     ├─ facebook_logo.png
│     ├─ instagram_logo.png
│     └─ linkedin-logo.png
```


## Requirements
- Python 3.10+ (recommended)
- pip

Python dependencies (installed via `requirements.txt`):
- Flask~=3.1.2
- qrcode


## Setup & run (local)
1) Clone or download this repository.

2) Create and activate a virtual environment (Windows PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies:
```
pip install -r requirements.txt
```

4) (Optional) Configure environment variables:
- `SECRET_KEY` — overrides the default development key.

You can set it in PowerShell for the current session:
```
$env:SECRET_KEY = "your-strong-secret"
```

5) Start the app:
```
python app.py
```

6) Open the app in your browser:
- http://127.0.0.1:5000/


## Using the Web UI
Each social page contains a form with:
- Profile URL
- Display name
- Options:
  - Use shortlink (on/off)
  - Rounded corners (on/off)
  - Corner radius (default 40)
  - QR size (default 300)

Submit to preview the QR and use the Download button to save a PNG.


## HTTP API
Endpoint: `POST /api/generate`

Content-Type: `application/json`

Request body fields:
- `platform` — one of `facebook`, `instagram`, `linkedin` (required)
- `profile_url` — full profile URL or handle (required)
- `display_name` — text to render under the QR (required)
- `use_shortlink` — boolean (default: true)
- `rounded_corners` — boolean (default: false)
- `corner_radius` — integer, pixels (default: 40)
- `qr_size` — integer, pixels (default: 300)

Example cURL:
```
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "profile_url": "https://instagram.com/myhandle",
    "display_name": "My Brand",
    "use_shortlink": true,
    "rounded_corners": true,
    "corner_radius": 40,
    "qr_size": 300
  }'
```

Successful response (truncated example):
```
{
  "success": true,
  "qr_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "shortlink": "instagram.com/myhandle",
  "full_url": "https://instagram.com/myhandle"
}
```

Errors:
- 400 with `{ "error": "Invalid platform" }` for unsupported `platform`.
- 500 with `{ "error": "<message>" }` on unexpected errors.


## Download endpoint (from UI)
The UI uses `POST /download/<platform>` to download the generated QR as a PNG. It accepts the same form fields as the social pages.


## Implementation notes
- QR generation and styling are handled in `app/utils/social_qr.py` via the `SocialQRGenerator` class.
- Shortlinks are formatted by `app/utils/url_shortener.py` and converted to full URLs when needed.
- Flask app factory is defined in `app/__init__.py`; routes are registered via a blueprint in `app/routes.py`.


## Localization
- UI strings are currently in Bulgarian (e.g., form labels, messages). The backend/route names and API remain language-agnostic.


## License
Specify your preferred license (e.g., MIT) here.
