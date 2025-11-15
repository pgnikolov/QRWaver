from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
import base64
import qrcode
import qrcode.image.svg

RGB = Tuple[int, int, int]


def _parse_hex_color(s: str, default: RGB) -> RGB:
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
    format: str = "svg"
    frame: Optional[Dict[str, Any]] = None


class QRService:
    _EC_MAP = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    from app.services.qr_types import (
        build_phone_payload,
        build_email_payload,
        build_location_payload,
        build_vcard_payload,
        build_youtube_payload,
        build_event_payload,
        build_crypto_payload,
        build_appstore_payload,
        build_social_payload,
    )
    from app.services.qr_types.url_qr import build_url_payload
    from app.services.qr_types.text_qr import build_text_payload
    from app.services.qr_types.wifi_qr import build_wifi_payload

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

    # ---------------- SVG RENDER ----------------
    def render_qr_svg(self, payload: str, settings: QRRenderSettings) -> str:
        qr = qrcode.QRCode(
            version=None,
            error_correction=self._EC_MAP.get(settings.error_correction.upper(), qrcode.constants.ERROR_CORRECT_H),
            box_size=10,
            border=settings.border,
        )

        qr.add_data(payload)
        qr.make(fit=True)

        fg_r, fg_g, fg_b = _parse_hex_color(settings.color, (0, 0, 0))
        bg_r, bg_g, bg_b = _parse_hex_color(settings.background, (255, 255, 255))

        img = qr.make_image(
            image_factory=qrcode.image.svg.SvgPathImage,
            fill_color=f"rgb({fg_r},{fg_g},{fg_b})",
            back_color=f"rgb({bg_r},{bg_g},{bg_b})"
        )

        buf = BytesIO()
        img.save(buf)
        return buf.getvalue().decode("utf-8")

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
        )

        # ✅ GENERATE SVG QR
        svg_text = self.render_qr_svg(payload, opts)

        svg_b64 = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
        data_uri = f"data:image/svg+xml;base64,{svg_b64}"

        filename = f"qrwaver_{qr_type}_{datetime.now():%Y-%m-%dT%H-%M-%S}.svg"

        return {
            "success": True,
            "image": data_uri,
            "mime": "image/svg+xml",
            "payload": payload,
            "filename": filename,
            "width": opts.size,
            "height": opts.size,
        }
