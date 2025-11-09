from flask import Blueprint, render_template, abort

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")

VALID_TYPES = {
    "url", "text", "wifi", "email", "phone", "vcard",
    "location", "youtube", "event", "crypto",
    "appstore", "googleplay", "menu",
    "facebook", "instagram", "linkedin",
    "tiktok", "twitter"
}

@qr_bp.route("/<qr_type>")
def qr_editor(qr_type):

    qr_type_lower = qr_type.lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if qr_type_lower not in VALID_TYPES:
        abort(404)

    template_path = f"qr_editors/qr_{qr_type_lower}.html"
    return render_template(template_path, qr_type=qr_type_lower)
