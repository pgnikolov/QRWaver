import os
import re
import secrets
import string
from datetime import datetime, UTC
from typing import Dict, Optional, Tuple

import requests
from flask import Request
from sqlalchemy import func

from app.extensions.extensions import db
from app.models.qr_code import QRCode
from app.models.qr_scan import QRScan


class AnalyticsService:
    """
    Lightweight analytics helper for scan tracking and stats aggregation.

    - generate_slug(): create a short unique id for /s/<slug>
    - enrich_request(): extract ip/referrer/utm/ua, and optional geo lookup
    - log_scan(): persist QRScan row and increment counters on QRCode
    - get_stats(): aggregate totals, daily series, and simple breakdowns
    """

    def __init__(self):
        self.ipinfo_token = os.getenv("IPINFO_TOKEN")

    # -------------------------
    # Slug generation
    # -------------------------
    def generate_slug(self, length: int = 8) -> str:
        alphabet = string.ascii_letters + string.digits
        while True:
            slug = "".join(secrets.choice(alphabet) for _ in range(length))
            if not QRCode.query.filter_by(slug=slug).first():
                return slug

    # -------------------------
    # Enrichment
    # -------------------------
    def _detect_device(self, ua: str) -> Tuple[str, str, str]:
        ua = ua or ""
        ual = ua.lower()
        # naive device type
        if any(s in ual for s in ["bot", "crawler", "spider"]):
            device = "bot"
        elif "mobile" in ual or "iphone" in ual or "android" in ual:
            device = "mobile"
        elif "ipad" in ual or "tablet" in ual:
            device = "tablet"
        else:
            device = "desktop"

        # naive OS parsing
        if "windows" in ual:
            os = "Windows"
        elif "mac os" in ual or "macintosh" in ual:
            os = "macOS"
        elif "android" in ual:
            os = "Android"
        elif "iphone" in ual or "ios" in ual or "ipad" in ual:
            os = "iOS"
        elif "linux" in ual:
            os = "Linux"
        else:
            os = "Other"

        # naive browser parsing
        if "chrome" in ual and "edg" not in ual and "opr" not in ual:
            browser = "Chrome"
        elif "safari" in ual and "chrome" not in ual:
            browser = "Safari"
        elif "firefox" in ual:
            browser = "Firefox"
        elif "edg" in ual:
            browser = "Edge"
        elif "opr" in ual or "opera" in ual:
            browser = "Opera"
        else:
            browser = "Other"

        return device, os, browser

    def _client_ip(self, request: Request) -> Optional[str]:
        h = request.headers
        ip = (
            h.get("CF-Connecting-IP")
            or h.get("X-Real-IP")
            or (h.get("X-Forwarded-For") or ":").split(",")[0].strip()
            or request.remote_addr
        )
        # basic IPv4/IPv6 validation
        if ip and len(ip) <= 45:
            return ip
        return None

    def _geo_lookup(self, ip: Optional[str]) -> Dict[str, Optional[str]]:
        if not ip or not self.ipinfo_token:
            return {"country": None, "region": None, "city": None, "lat": None, "lon": None}
        try:
            resp = requests.get(f"https://ipinfo.io/{ip}?token={self.ipinfo_token}", timeout=2)
            if resp.status_code != 200:
                return {"country": None, "region": None, "city": None, "lat": None, "lon": None}
            data = resp.json()
            loc = data.get("loc", ",")
            lat, lon = None, None
            if loc and "," in loc:
                parts = loc.split(",")
                if len(parts) == 2:
                    try:
                        lat = float(parts[0])
                        lon = float(parts[1])
                    except Exception:
                        lat = lon = None
            return {
                "country": data.get("country"),
                "region": data.get("region"),
                "city": data.get("city"),
                "lat": lat,
                "lon": lon,
            }
        except Exception:
            return {"country": None, "region": None, "city": None, "lat": None, "lon": None}

    def enrich_request(self, request: Request) -> Dict[str, Optional[str]]:
        ua = request.headers.get("User-Agent")
        ref = request.headers.get("Referer")
        ip = self._client_ip(request)
        device, os_name, browser = self._detect_device(ua or "")

        # UTM params
        args = request.args or {}
        utm = {
            "utm_source": args.get("utm_source"),
            "utm_medium": args.get("utm_medium"),
            "utm_campaign": args.get("utm_campaign"),
            "utm_term": args.get("utm_term"),
            "utm_content": args.get("utm_content"),
        }

        geo = self._geo_lookup(ip)

        return {
            "ip": ip,
            "ua_raw": ua,
            "referrer": ref,
            "device_type": device,
            "os": os_name,
            "browser": browser,
            **utm,
            **geo,
        }

    # -------------------------
    # Persistence
    # -------------------------
    def log_scan(self, qr: QRCode, enriched: Dict[str, Optional[str]]):
        scan = QRScan(
            qr_id=qr.id,
            ip=enriched.get("ip"),
            country=enriched.get("country"),
            region=enriched.get("region"),
            city=enriched.get("city"),
            lat=enriched.get("lat"),
            lon=enriched.get("lon"),
            ua_raw=enriched.get("ua_raw"),
            device_type=enriched.get("device_type"),
            os=enriched.get("os"),
            browser=enriched.get("browser"),
            referrer=enriched.get("referrer"),
            utm_source=enriched.get("utm_source"),
            utm_medium=enriched.get("utm_medium"),
            utm_campaign=enriched.get("utm_campaign"),
            utm_term=enriched.get("utm_term"),
            utm_content=enriched.get("utm_content"),
        )
        db.session.add(scan)

        # Increment counters on QRCode
        qr.scan_count = (qr.scan_count or 0) + 1
        qr.last_scan_at = datetime.now(UTC)
        db.session.add(qr)
        db.session.commit()

    # -------------------------
    # Aggregations
    # -------------------------
    def get_stats(self, qr_id: int, start_iso: Optional[str], end_iso: Optional[str], group: str = "day") -> Dict:
        q = QRScan.query.filter(QRScan.qr_id == qr_id)
        # Time range filters
        if start_iso:
            try:
                start_dt = datetime.fromisoformat(start_iso)
                q = q.filter(QRScan.ts >= start_dt)
            except Exception:
                pass
        if end_iso:
            try:
                end_dt = datetime.fromisoformat(end_iso)
                q = q.filter(QRScan.ts <= end_dt)
            except Exception:
                pass

        total = q.count()

        # Daily series
        series_rows = (
            db.session.query(func.date(QRScan.ts), func.count())
            .filter(QRScan.qr_id == qr_id)
            .group_by(func.date(QRScan.ts))
            .order_by(func.date(QRScan.ts))
            .all()
        )
        series = [{"date": d, "count": c} for d, c in series_rows]

        # Breakdowns
        def top_by(field, limit=10):
            rows = (
                db.session.query(getattr(QRScan, field), func.count())
                .filter(QRScan.qr_id == qr_id)
                .group_by(getattr(QRScan, field))
                .order_by(func.count().desc())
                .limit(limit)
                .all()
            )
            return [{field: (v or "(unknown)"), "count": c} for v, c in rows]

        by_country = top_by("country")
        by_device = top_by("device_type")
        by_browser = top_by("browser")
        by_referrer = top_by("referrer")

        # UTM breakdown as nested dict of counts
        utm_fields = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]
        utm = {f: top_by(f) for f in utm_fields}

        return {
            "totals": {"scans": total},
            "series": series,
            "by_country": by_country,
            "by_device": by_device,
            "by_browser": by_browser,
            "by_referrer": by_referrer,
            "utm": utm,
        }
