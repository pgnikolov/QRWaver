from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

import base64
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw

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


# optional: rounded corners from your utils if present
try:
    from app.utils.style_utils import add_rounded_corners as _rc
except Exception:
    _rc = None  # fallback below


RGBA = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]


def _parse_hex_color(s: str, default: RGB) -> RGB:
    """Parse '#RRGGBB' → (R,G,B)."""
    try:
        s = (s or "").strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return default
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return r, g, b
    except Exception:
        return default


def _rounded_corners(img: Image.Image, radius: int) -> Image.Image:
    """Local fallback if app.utils.style_utils is missing."""
    if radius <= 0:
        return img
    if _rc:
        return _rc(img, radius)  # use your project util if available

    # generic fallback
    mask = Image.new("L", img.size, 0)
    corner = Image.new("L", (radius * 2, radius * 2), 0)
    d = ImageDraw.Draw(corner)
    d.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    w, h = img.size
    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(corner.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    mask.paste(corner.crop((0, radius, radius, radius * 2)), (0, h - radius))
    mask.paste(corner.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    # edges
    draw = ImageDraw.Draw(mask)
    draw.rectangle((radius, 0, w - radius, h), fill=255)
    draw.rectangle((0, radius, w, h - radius), fill=255)

    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


@dataclass
class QRRenderSettings:
    size: int = 512                 # final square size in px
    color: str = "#000000"          # foreground color
    background: str = "#FFFFFF"     # background color
    error_correction: str = "H"     # L/M/Q/H
    border: int = 4                 # quiet zone
    rounded_corners: bool = False
    corner_radius: int = 24
    overlay_logo_path: Optional[str] = None  # static path or absolute
    format: str = "png"             # 'png' (now), 'svg' (later)


class QRService:
    """Single entry point for: validation → payload build → QR render → base64."""

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

    def validate(self, qr_type: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Return dict of field->error; empty dict means OK."""
        qr_type = (qr_type or "").strip().lower()
        errors: Dict[str, str] = {}

        if qr_type == "url":
            url = (data or {}).get("url", "").strip()
            if not url:
                errors["url"] = "URL is required."
            elif not (url.startswith("http://") or url.startswith("https://")):
                errors["url"] = "URL must start with http:// or https://"
            return errors

        if not data:
            errors["data"] = "Payload is required."
        return errors

    # ---------------- Payload builders ----------------

    def build_payload(self, qr_type: str, data: Dict[str, Any]) -> str:
        """Builds the payload string by delegating to the correct builder."""
        qr_type = (qr_type or "").strip().lower()
        builder = self.PAYLOAD_BUILDERS.get(qr_type)

        if not builder:
            raise ValueError(f"Unsupported QR type: {qr_type}")

        return builder(data)

    # ---------------- Rendering ----------------

    def render_qr_png(self, payload: str, settings: QRRenderSettings) -> Image.Image:
        """Render a QR as PIL image with styling (PNG pipeline)."""
        ec = self._EC_MAP.get((settings.error_correction or "H").upper(), ERROR_CORRECT_H)
        qr = qrcode.QRCode(version=None, error_correction=ec, box_size=10, border=settings.border)
        qr.add_data(payload)
        qr.make(fit=True)

        fg = _parse_hex_color(settings.color, (0, 0, 0))
        bg = _parse_hex_color(settings.background, (255, 255, 255))

        img = qr.make_image(fill_color=fg, back_color=bg).convert("RGBA")
        img = img.resize((settings.size, settings.size), Image.Resampling.LANCZOS)

        # optional overlay logo (center)
        if settings.overlay_logo_path:
            try:
                logo = Image.open(settings.overlay_logo_path).convert("RGBA")
                max_side = max(48, settings.size // 5)
                logo.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

                pad = max(6, max_side // 10)
                pad_img = Image.new(
                    "RGBA",
                    (logo.width + pad * 2, logo.height + pad * 2),
                    (255, 255, 255, 230),
                )
                pad_img.paste(logo, (pad, pad), logo)

                x = (settings.size - pad_img.width) // 2
                y = (settings.size - pad_img.height) // 2
                img.alpha_composite(pad_img, (x, y))
            except Exception:
                pass  # ignore logo failures

        if settings.rounded_corners and settings.corner_radius > 0:
            img = _rounded_corners(img, int(settings.corner_radius))

        return img

    def to_base64_png(self, img: Image.Image) -> str:
        """Return data URI (base64 PNG)."""
        buf = BytesIO()
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    # ---------------- High-level API ----------------

    def generate(
        self,
        qr_type: str,
        data: Dict[str, Any],
        settings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate, build payload and return base64 PNG + meta."""
        errs = self.validate(qr_type, data)
        if errs:
            return {"success": False, "errors": errs}

        payload = self.build_payload(qr_type, data)
        opts = QRRenderSettings(
            size=int(settings.get("size", 512)),
            color=str(settings.get("color", "#000000")),
            background=str(settings.get("background", "#FFFFFF")),
            error_correction=str(settings.get("error_correction", "H")),
            border=int(settings.get("border", 4)),
            rounded_corners=bool(settings.get("rounded_corners", False)),
            corner_radius=int(settings.get("corner_radius", 24)),
            overlay_logo_path=settings.get("overlay_logo_path"),
            format=str(settings.get("format", "png")).lower(),
        )

        image = self.render_qr_png(payload, opts)
        data_uri = self.to_base64_png(image)

        # auto filename
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"qrweaver_{qr_type}_{timestamp}.png"

        return {
            "success": True,
            "image": data_uri,
            "mime": "image/png",
            "width": image.width,
            "height": image.height,
            "payload": payload,
            "filename": filename,
        }
