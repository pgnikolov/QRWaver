from datetime import datetime, UTC
from app.extensions.extensions import db


class QRScan(db.Model):
    __tablename__ = "qr_scans"

    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.Integer, db.ForeignKey('qr_codes.id'), nullable=False, index=True)

    ts = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

    # Networking / geo (geo fields optional for now)
    ip = db.Column(db.String(45), nullable=True)
    country = db.Column(db.String(64), nullable=True)
    region = db.Column(db.String(64), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)

    # User agent parsing (simple for now)
    ua_raw = db.Column(db.Text, nullable=True)
    device_type = db.Column(db.String(16), nullable=True)  # mobile/desktop/tablet/bot
    os = db.Column(db.String(32), nullable=True)
    browser = db.Column(db.String(32), nullable=True)

    referrer = db.Column(db.Text, nullable=True)
    utm_source = db.Column(db.String(64), nullable=True)
    utm_medium = db.Column(db.String(64), nullable=True)
    utm_campaign = db.Column(db.String(64), nullable=True)
    utm_term = db.Column(db.String(64), nullable=True)
    utm_content = db.Column(db.String(64), nullable=True)
