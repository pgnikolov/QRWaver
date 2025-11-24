from datetime import datetime, UTC
from app.extensions.extensions import db


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("qr_codes", lazy=True))

    qr_type = db.Column(db.String(30), nullable=False)  # e.g. url, wifi, vcard, text
    payload = db.Column(db.Text, nullable=False)  # original data used to generate QR
    file_path = db.Column(db.String(255), nullable=False)  # relative path /static/qr/...

    # Tracking (analytics)
    slug = db.Column(db.String(32), unique=True, nullable=True)  # short id for /s/<slug>
    is_trackable = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    scan_count = db.Column(db.Integer, default=0)
    last_scan_at = db.Column(db.DateTime(timezone=True), nullable=True)
