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
    """
    Parses a string representing a hexadecimal color and converts it into an RGB tuple. If the input string is invalid or
    cannot be parsed, a default RGB value is returned.

    :param s: A string representing a hexadecimal color code. It may include the leading '#'
        character and can use a shorthand format (e.g., "#abc" equivalent to "#aabbcc").
    :param default: A default RGB tuple to return if the input string is invalid or cannot be parsed.
    :return: A tuple of three integers representing the RGB color, where each integer ranges
        from 0 to 255.
    """
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
    """
    Represents the settings for rendering a QR code.

    This class is used to define and customize various parameters for QR code
    generation, such as dimensions, colors, error correction level, and more. It
    can also include additional optional elements like a logo overlay or a frame.
    The settings provided by this class can be used to generate a styled and
    functional QR code suitable for different purposes.

    :ivar size: The size of the QR code in pixels.
    :type size: int
    :ivar color: The color of the QR code in hexadecimal format.
    :type color: str
    :ivar background: The background color of the QR code in hexadecimal format.
    :type background: str
    :ivar error_correction: The error correction level of the QR code. Possible
        values are "L", "M", "Q", or "H".
    :type error_correction: str
    :ivar border: The size of the border around the QR code (measured in modules).
    :type border: int
    :ivar overlay_logo_path: The file path for an optional overlay logo to be
        placed in the center of the QR code.
    :type overlay_logo_path: Optional[str]
    :ivar format: The file format for the rendered QR code (e.g., "png").
    :type format: str
    :ivar frame: A dictionary representing an optional SVG frame for the QR code,
        which is typically handled by the frontend.
    :type frame: Optional[Dict[str, Any]]
    """
    size: int = 512
    color: str = "#000000"
    background: str = "#FFFFFF"
    error_correction: str = "H"
    border: int = 4
    overlay_logo_path: Optional[str] = None
    format: str = "png"
    frame: Optional[Dict[str, Any]] = None   # FRONTEND handles SVG frame!


class QRService:
    """
    QRService handles the creation, validation, and rendering of various types of QR codes.

    This class provides methods to validate input data, construct payloads based on the
    specified QR code type, render QR codes with customizable styling, and generate encoded
    images in a consumable format.

    :ivar PAYLOAD_BUILDERS: Mapping of QR code types to their respective payload builders.
    :ivar _EC_MAP: Internal mapping of error correction levels to QRCode constants in the
                   qrcode library.
    """
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
