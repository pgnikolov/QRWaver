"""
QR Type payload builders registry.

Each module defines a `build_<type>_payload(data: dict) -> str`
function that prepares the correct text payload for QR encoding.
"""

from .url_qr import build_url_payload
from .vcard_qr import build_vcard_payload
from .wifi_qr import build_wifi_payload
from .email_qr import build_email_payload
from .phone_qr import build_phone_payload
from .text_qr import build_text_payload
from .social_qr import build_social_payload
from .youtube_qr import build_youtube_payload

# Registry map for the QR service
PAYLOAD_BUILDERS = {
    "url": build_url_payload,
    "vcard": build_vcard_payload,
    "wifi": build_wifi_payload,
    "email": build_email_payload,
    "phone": build_phone_payload,
    "text": build_text_payload,
    "social": build_social_payload,
    "youtube": build_youtube_payload
}
