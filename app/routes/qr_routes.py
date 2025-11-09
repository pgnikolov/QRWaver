from flask import Blueprint, render_template, abort

qr_bp = Blueprint("qr", __name__)

@qr_bp.route("/<qr_type>")
def qr_editor(qr_type):
    """Temporary placeholder for all QR type editors."""
    supported = [
        "url", "vcard", "wifi", "text", "email", "phone",
        "location", "event", "youtube", "appstore", "crypto", "menu", "social"
    ]
    if qr_type not in supported:
        abort(404)
    return render_template("qr_editor_placeholder.html", qr_type=qr_type)
