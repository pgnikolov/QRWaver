"""QR generation and upload service.

This module centralizes logic for building text payloads for various QR types,
rendering QR codes in multiple formats (SVG/PNG/JPG), and uploading the
resulting images to the configured object storage (Cloudflare R2).
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any, Dict
import qrcode
import qrcode.image.svg

from app.services.r2_service import R2Service


@dataclass
class QRRenderSettings:
    size: int = 512


class QRService:
    """High-level QR service.

    - `build_payload(...)` -> string (delegates to `qr_types/*` helpers)
    - Generates QR images in SVG/PNG/JPG
    - Uploads finished images to R2
    """

    # ------------------------------------------------
    # PAYLOAD BUILDERS
    # ------------------------------------------------
    from app.services.qr_types import (
        build_phone_payload,
        build_email_payload,
        build_vcard_payload,
        build_youtube_payload,
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
        "youtube": build_youtube_payload,
        "social": build_social_payload,
    }

    def build_payload(self, qr_type: str, data: Any) -> str:
        qr_type = (qr_type or "").strip().lower()
        builder = self.PAYLOAD_BUILDERS.get(qr_type)
        if not builder:
            raise ValueError(f"Unsupported QR type: {qr_type}")
        return builder(data)

    # ------------------------------------------------
    # RAW QR GENERATION
    # ------------------------------------------------
    def _generate_svg_bytes(self, text: str, size: int = 512) -> bytes:
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(image_factory=factory)
        buf = io.BytesIO()
        img.save(buf)
        return buf.getvalue()

    def _generate_png_bytes(self, text: str, size: int = 512) -> bytes:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img = img.resize((size, size))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _generate_jpg_bytes(self, text: str, size: int = 512) -> bytes:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img = img.resize((size, size))

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    # ------------------------------------------------
    # MAIN API — generate and upload to R2
    # ------------------------------------------------
    def create_and_upload_qr(
        self,
        user_id: int,
        payload: str,
        fmt: str = "svg",
        size: int = 512,
    ) -> Dict[str, Any]:
        """Create a QR image for a given payload and upload it.

        Args:
            user_id: Owner id, used for organizing storage paths.
            payload: Already constructed text (e.g., URL, WIFI:, VCARD, ...).
            fmt: One of "svg", "png", "jpg".
            size: Output size in pixels (for raster formats) or nominal size.

        Returns:
            A dictionary with keys: `success`, `url`, `mime`, `payload`,
            `filename`, `width`, `height`.
        """

        fmt = (fmt or "svg").lower()

        if fmt == "svg":
            mime = "image/svg+xml"
            ext = "svg"
            qr_bytes = self._generate_svg_bytes(payload, size=size)
            # `upload_svg` expects a string
            url = R2Service.upload_svg(user_id, qr_bytes.decode("utf-8"))

        elif fmt == "png":
            mime = "image/png"
            ext = "png"
            qr_bytes = self._generate_png_bytes(payload, size=size)
            url = R2Service.upload_image(user_id, qr_bytes, ext)

        elif fmt in ("jpg", "jpeg"):
            mime = "image/jpeg"
            ext = "jpg"
            qr_bytes = self._generate_jpg_bytes(payload, size=size)
            url = R2Service.upload_image(user_id, qr_bytes, ext)

        else:
            raise ValueError("Unsupported format. Use svg, png, jpg.")

        return {
            "success": True,
            "url": url,
            "mime": mime,
            "payload": payload,
            "filename": url.rsplit("/", 1)[-1],
            "width": size,
            "height": size,
        }
