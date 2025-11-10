from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

import base64
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

from app.services.qr_types import (
    build_phone_payload,
    build_email_payload,
    build_location_payload,
    build_vcard_payload,
    build_youtube_payload,
    build_event_payload,
    build_crypto_payload,
    build_appstore_payload,
    build_menu_payload,
    build_social_payload,
)
from app.services.qr_types.url_qr import build_url_payload
from app.services.qr_types.text_qr import build_text_payload
from app.services.qr_types.wifi_qr import build_wifi_payload


RGB = Tuple[int, int, int]


def _parse_hex_color(s: str, default: RGB) -> RGB:
    """'#RRGGBB' -> (R,G,B)."""
    if not s:
        return default
    s = s.strip().lstrip("#")

    if len(s) == 3:
        s = "".join(c * 2 for c in s)

    if len(s) != 6:
        return default

    try:
        return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
    except:
        return default


@dataclass
class QRRenderSettings:
    size: int = 512
    color: str = "#000000"
    background: str = "#FFFFFF"
    error_correction: str = "H"
    border: int = 4
    overlay_logo_path: Optional[str] = None
    format: str = "png"
    frame: Optional[Dict[str, Any]] = None   # FRONTEND handles SVG frame!


class QRService:

    _EC_MAP = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    PAYLOAD_BUILDERS = {
        "url": build_url_payload,
        "text": build_text_payload,
        "wifi": build_wifi_payload,
        "email": build_email_payload,
        "phone": build_phone_payload,
        "vcard": build_vcard_payload,
        "location": build_location_payload,
        "youtube": build_youtube_payload,
        "event": build_event_payload,
        "crypto": build_crypto_payload,
        "appstore": build_appstore_payload,
        "menu": build_menu_payload,
        "social": build_social_payload,
    }

    # ---------------- VALIDATION ----------------
    def validate(self, qr_type: str, data: Any) -> Dict[str, str]:
        qr_type = (qr_type or "").strip().lower()
        errors: Dict[str, str] = {}

        if qr_type == "url":
            url = ""
            if isinstance(data, dict):
                url = (data.get("url") or "").strip()
            elif isinstance(data, str):
                url = data.strip()

            if not url:
                errors["url"] = "URL required."
            elif not (url.startswith("http://") or url.startswith("https://")):
                errors["url"] = "URL must start with http:// or https://"

            return errors

        if data is None or (isinstance(data, str) and not data.strip()):
            errors["data"] = "Payload required."

        return errors

    # ---------------- PAYLOAD ----------------
    def build_payload(self, qr_type: str, data: Any) -> str:
        builder = self.PAYLOAD_BUILDERS.get(qr_type)
        if not builder:
            raise ValueError(f"Unsupported QR type: {qr_type}")
        return builder(data)

    # ---------------- RENDER ----------------
    def render_qr_png(self, payload: str, settings: QRRenderSettings) -> Image.Image:
        ec = self._EC_MAP.get(settings.error_correction.upper(), ERROR_CORRECT_H)

        qr = qrcode.QRCode(
            version=None,
            error_correction=ec,
            box_size=10,
            border=settings.border
        )
        qr.add_data(payload)
        qr.make(fit=True)

        fg = _parse_hex_color(settings.color, (0, 0, 0))
        bg = _parse_hex_color(settings.background, (255, 255, 255))

        # ✅ CLEAN QR (no frame, no rounded corners, nothing)
        img = qr.make_image(
            fill_color=fg,
            back_color=bg
        ).convert("RGBA")

        # Resize to requested output size
        img = img.resize((settings.size, settings.size), Image.Resampling.LANCZOS)

        # ✅ FRAME IS HANDLED IN FRONTEND
        return img

    # ---------------- TO BASE64 ----------------
    def to_base64_png(self, img: Image.Image) -> str:
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    # ---------------- MAIN API ----------------
    def generate(self, qr_type: str, data: Any, settings: Dict[str, Any]) -> Dict[str, Any]:

        errors = self.validate(qr_type, data)
        if errors:
            return {"success": False, "errors": errors}

        payload = self.build_payload(qr_type, data)

        opts = QRRenderSettings(
            size=int(settings.get("size", 512)),
            color=str(settings.get("color", "#000000")),
            background=str(settings.get("background", "#FFFFFF")),
            error_correction=str(settings.get("error_correction", "H")),
            border=int(settings.get("border", 4)),
            overlay_logo_path=settings.get("overlay_logo_path"),
            format=str(settings.get("format", "png")).lower(),
            frame=settings.get("frame") or {},   # frontend SVG overlay
        )

        img = self.render_qr_png(payload, opts)
        data_uri = self.to_base64_png(img)

        filename = f"qrwaver_{qr_type}_{datetime.now():%Y-%m-%dT%H-%M-%S}.png"

        return {
            "success": True,
            "image": data_uri,
            "mime": "image/png",
            "width": img.width,
            "height": img.height,
            "payload": payload,
            "filename": filename,
        }
