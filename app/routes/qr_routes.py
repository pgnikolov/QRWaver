"""Routes for QR editor pages.

Renders the appropriate editor template based on the QR type in the URL.
Performs basic normalization/validation of the type segment before rendering.
"""

from flask import Blueprint, render_template, abort

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")

VALID_TYPES = {
    "url", "text", "wifi", "email", "phone", "vcard",
    "youtube", "facebook", "instagram", "linkedin",
    "tiktok", "twitter"
}


@qr_bp.route("/<qr_type>")
def qr_editor(qr_type):
    """
    Handles the QR editor route and dynamically renders the appropriate QR editor
    template based on the provided QR type. Verifies the QR type against a predefined
    list of valid types before generating the editor page.

    :param qr_type: The type of QR to edit. This parameter is extracted from the
                    request URL and converted to lowercase, with special characters
                    and spaces removed.
    :type qr_type: str
    :return: The HTML template for the specified QR type editor.
    :rtype: flask.Response
    :raises 404: If the provided QR type is not in the predefined list of valid types.
    """
    qr_type_lower = qr_type.lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if qr_type_lower not in VALID_TYPES:
        abort(404)

    template_path = f"qr_editors/qr_{qr_type_lower}.html"
    return render_template(template_path, qr_type=qr_type_lower)
