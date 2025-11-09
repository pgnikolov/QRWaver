from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

import base64
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

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

try:
    from app.utils.style_utils import add_rounded_corners as _rc
except Exception:
    _rc = None


RGB = Tuple[int, int, int]


def _parse_hex_color(s: str, default: RGB) -> RGB:
    """'#RRGGBB' | '#RGB' -> (R, G, B)."""
    if not s:
        return default
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return default
    try:
        return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return default


def _rounded_corners(img: Image.Image, radius: int) -> Image.Image:

    if radius <= 0:
        return img
    if _rc:
        return _rc(img, radius)

    mask = Image.new("L", img.size, 0)
    corner = Image.new("L", (radius * 2, radius * 2), 0)
    d = ImageDraw.Draw(corner)
    d.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    w, h = img.size
    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(corner.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    mask.paste(corner.crop((0, radius, radius, radius * 2)), (0, h - radius))
    mask.paste(corner.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    draw = ImageDraw.Draw(mask)
    draw.rectangle((radius, 0, w - radius, h), fill=255)
    draw.rectangle((0, radius, w, h - radius), fill=255)

    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def add_frame_rounded(qr_img: Image.Image, text: str, color: str) -> Image.Image:
    frame_rgb = _parse_hex_color(color, (0, 0, 0))
    frame_rgba = (*frame_rgb, 255)

    qr_w, qr_h = qr_img.size
    border = 40
    pill_h = 65

    new_w = qr_w + border * 2
    new_h = qr_h + border * 2 + pill_h + 10

    canvas = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    corner_radius = 45
    draw.rounded_rectangle(
        (0, 0, new_w, qr_h + border * 2),
        radius=corner_radius,
        outline=frame_rgba,
        width=16,
    )

    canvas.paste(qr_img, (border, border), qr_img)

    pill_top = qr_h + border * 2 - 8
    pill_rect = (20, pill_top, new_w - 20, pill_top + pill_h)
    draw.rounded_rectangle(pill_rect, radius=32, fill=frame_rgba)

    try:
        fnt = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        fnt = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (new_w - tw) // 2
    ty = pill_rect[1] + (pill_h - th) // 2
    draw.text((tx, ty), text, fill="white", font=fnt)

    return canvas


@dataclass
class QRRenderSettings:
    size: int = 512
    color: str = "#000000"
    background: str = "#FFFFFF"
    error_correction: str = "H"
    border: int = 4
    rounded_corners: bool = False
    corner_radius: int = 24
    overlay_logo_path: Optional[str] = None
    format: str = "png"
    frame: Optional[Dict[str, Any]] = None  #


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

    # --------- Payload builder ---------
    def build_payload(self, qr_type: str, data: Any) -> str:
        builder = self.PAYLOAD_BUILDERS.get(qr_type)
        if not builder:
            raise ValueError(f"Unsupported QR type: {qr_type}")
        return builder(data)

    # --------- Рендер ---------
    def render_qr_png(self, payload: str, settings: QRRenderSettings) -> Image.Image:
        ec = self._EC_MAP.get((settings.error_correction or "H").upper(), ERROR_CORRECT_H)
        qr = qrcode.QRCode(version=None, error_correction=ec, box_size=10, border=settings.border)
        qr.add_data(payload)
        qr.make(fit=True)

        fg = _parse_hex_color(settings.color, (0, 0, 0))
        bg = _parse_hex_color(settings.background, (255, 255, 255))

        # Ако искаш прозрачен фон по дефолт – смени back_color на (255,255,255,0)
        img = qr.make_image(fill_color=fg, back_color=bg).convert("RGBA")
        img = img.resize((settings.size, settings.size), Image.Resampling.LANCZOS)

        if settings.rounded_corners and settings.corner_radius > 0:
            img = _rounded_corners(img, int(settings.corner_radius))

        # ---- FRAME (временен “rounded”) ----
        frame_cfg = settings.frame or {}
        frame_type = (
            frame_cfg.get("type")
            or frame_cfg.get("style")
            or frame_cfg.get("frame_type")
            or "none"
        )
        frame_type = str(frame_type).lower()

        if frame_type == "rounded":
            img = add_frame_rounded(
                img,
                text=str(frame_cfg.get("text", "SCAN ME")),
                color=str(frame_cfg.get("color", "#000000")),
            )
        # Другите видове (frame_2parts, frame_whole, frame_bag, frame_phone)
        # ще се реализират с SVG overlay. Тук просто не пипаме изображението.

        return img

    # --------- Base64 ---------
    def to_base64_png(self, img: Image.Image) -> str:
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    # --------- Основен API ---------
    def generate(self, qr_type: str, data: Any, settings: Dict[str, Any]) -> Dict[str, Any]:
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
            frame=settings.get("frame") or {},
        )

        image = self.render_qr_png(payload, opts)
        data_uri = self.to_base64_png(image)

        filename = f"qrwaver_{qr_type}_{datetime.now():%Y-%m-%dT%H-%M-%S}.png"

        return {
            "success": True,
            "image": data_uri,
            "mime": "image/png",
            "width": image.width,
            "height": image.height,
            "payload": payload,
            "filename": filename,
        }
