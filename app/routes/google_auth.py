from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

from app.config.settings import GOOGLE_CLIENT_ID
from app.services.user_service import UserService
from flask_jwt_extended import create_access_token, set_access_cookies

google_auth = Blueprint("google_auth", __name__, url_prefix="/auth")

@google_auth.post("/google")
def google_login():
    data = request.json
    token = data.get("id_token")

    if not token:
        return jsonify({"success": False, "error": "Missing id_token"}), 400

    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=60  # tolerate small time drift
        )

        email = idinfo["email"]

        # If user doesn't exist → create or attach google_id
        user = UserService.create_or_get_google_user(email=email, google_id=idinfo.get("sub"))

        # Generate JWT
        access_token = create_access_token(identity=user.id)

        response = jsonify({
            "success": True,
            "message": "Google login successful",
            "user_id": user.id,
            "email": email
        })

        # Set JWT cookie
        set_access_cookies(response, access_token)

        return response, 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
