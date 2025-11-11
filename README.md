
<p align="center">
  <img src="app/static/images/branding/logo_wordmark.png" width="300" alt="QRWaver Logo">
</p>

<h1 align="center">QRWaver</h1>
<p align="center"><strong>Open-Source QR Generator With Dynamic Styling</strong></p>
<p align="center">
  QR code generator with frames, dynamic styling, high-resolution output, and full API support.
</p>

---

## 🚀 Features

✅ Generate 15+ QR types (URL, Text, WiFi, Email, Phone, Crypto, App Store, Social & more)  
✅ Dynamic SVG frames with color customization  
✅ High-Resolution PNG & JPEG export (2200px)  
✅ True Vector SVG export  
✅ Clean API (POST /api/generate)  
✅ Frontend QR Composer (injects QR into SVG frame)  
✅ Fully responsive UI  
✅ No external dependencies like QR APIs — everything is local  
✅ Free & Open-Source

---

## 🧩 Project Structure

```

QRWaver/
├── app/
│   ├── config/
│   ├── routes/
│   ├── services/
│   │   ├── qr_types/
│   │   ├── qr_service.py
│   │   └── rate_limiter.py
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   │   ├── frames/
│   │   │   ├── frames_thumbs/
│   │   │   ├── icons/
│   │   │   └── branding/
│   │   └── js/
│   ├── templates/
│   │   ├── includes/
│   │   └── qr_editors/
│   ├── utils/
│   └── app.py
├── run.py
├── requirements.txt
└── README.md

````

---

## ✅ Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourname/QRWaver.git
cd QRWaver
````

### 2. Create virtual env

```bash
python3 -m venv venv
source venv/bin/activate   # Linux & macOS
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run development server

```bash
python run.py
```

Server starts on:

```
http://127.0.0.1:5000/
```

---

## 🧠 How It Works

QRWaver has a **hybrid rendering pipeline**:

### ✅ Step 1: Backend generates a clean QR PNG

Using **qrcode** + **Pillow**, backend returns base64 PNG:

```
QRService → render_qr_png() → to_base64_png()
```

### ✅ Step 2: Frontend injects PNG inside SVG frame

SVG templates include:

```svg
<rect id="QR_ZONE" x="38.5" y="38.5" width="966.57" height="966.57" />
```

JS replaces this zone with:

```html
<image href="data:image/png..." />
```

### ✅ Step 3: User exports as:

* **PNG/JPEG** → rendered at **2200px** in canvas
* **SVG** → 100% vector, untouched quality

---

## 📡 API Documentation

### **POST /api/generate**

**Example Request:**

```json
{
  "type": "text",
  "data": "Hello world",
  "settings": {
    "color": "#000000",
    "size": 512,
    "background": "#FFFFFF"
  }
}
```

**Example Response:**

```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "width": 512,
  "height": 512,
  "mime": "image/png"
}
```

---

## ✅ Supported QR Types

| Type       | Purpose               |
| ---------- | --------------------- |
| url        | Website link          |
| text       | Plain text            |
| wifi       | WiFi network          |
| email      | mailto:               |
| phone      | tel:                  |
| crypto     | BTC/ETH/etc           |
| appstore   | iOS app link          |
| googleplay | Android app link      |
| vcard      | Contact card          |
| social     | Instagram/TikTok/X/FB |
| youtube    | YouTube video/channel |
| event      | Calendar event        |
| location   | Geo coordinates       |
| menu       | Restaurants           |
| more…      | Easily extendable     |

---

## 🎨 Frames & Compositor (Frontend)

📁 Frames live in:

```
app/static/images/frames/*.svg
```

Each has:

```svg
<rect id="QR_ZONE" ... />  ✅ required
```

Frontend script:

✅ auto-detects QR_ZONE

✅ recolors frame

✅ injects QR

✅ converts to PNG for preview

✅ exports high-res output

---

## 🖼 High-Resolution Output

### ✅ PNG / JPEG

Rendered via Canvas:

* Always upscaled to **~2200px long side**
* Anti-aliased
* Perfect quality for printing

### ✅ SVG

Exported exactly as composed
→ pixel-perfect vector for professional use

---

## 🧪 Testing

Included pytest:

```
tests/test_api_v1.py
```

Run:

```bash
pytest
```

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Submit PR
4. All contributions welcome 🎉

---

## 📜 License

MIT — free for personal & commercial use.

---

## ❤️ Credits

Created with passion & caffeine.
Logo © QRWaver.
