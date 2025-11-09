from flask import Blueprint, render_template
from datetime import datetime, timezone


main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_now():
    return {'current_year': datetime.now(timezone.utc).year}

@main_bp.route("/")
def index():
    """Homepage with QR type selection."""
    return render_template("index.html", title="QRWeaver – Create Beautiful QR Codes")

@main_bp.route("/")
def about():
    return render_template("about.html", title="About QRWeaver")
