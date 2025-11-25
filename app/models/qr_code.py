"""Database model representing a generated QR code.

Each record holds the original payload (e.g., a URL), a reference to the
rendered QR image location, and optional tracking fields used for analytics.
"""

from datetime import datetime, UTC
from app.extensions.extensions import db


class QRCode(db.Model):
    """Persistent QR code entity.

    Attributes:
        id: Primary key.
        user_id: Foreign key referencing the owning `User`.
        user: Relationship to the `User` model.
        qr_type: Logical type of the QR (e.g., "url", "wifi", "text").
        payload: The original content used to generate the QR.
        file_path: Public URL (or path) to the rendered QR image.
        slug: Short identifier used in trackable short links (`/s/<slug>`).
        is_trackable: Whether requests to the short link should be logged.
        created_at: UTC timestamp when the QR was created.
        scan_count: Incremented number of recorded scans.
        last_scan_at: UTC timestamp of the last scan (if any).
    """
    __tablename__ = "qr_codes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("qr_codes", lazy=True))

    qr_type = db.Column(db.String(30), nullable=False)  # e.g., url, wifi, vcard, text
    payload = db.Column(db.Text, nullable=False)  # original data used to generate QR
    file_path = db.Column(db.String(255), nullable=False)  # full public URL in v1

    # Tracking (analytics)
    slug = db.Column(db.String(32), unique=True, nullable=True)  # short id for /s/<slug>
    is_trackable = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    scan_count = db.Column(db.Integer, default=0)
    last_scan_at = db.Column(db.DateTime(timezone=True), nullable=True)
