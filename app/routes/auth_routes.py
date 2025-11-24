from flask import Blueprint, request, jsonify, current_app, render_template
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from app.schemas.user_schema import UserRegisterSchema, UserLoginSchema
from app.services.user_service import UserService
from pydantic import ValidationError
import google.oauth2.id_token
import google.auth.transport.requests
from flask import redirect, url_for
from app.config.settings import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI, GOOGLE_CLIENT_SECRET

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    try:
        data = UserRegisterSchema(**request.json)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.errors()}), 400

    if UserService.get_by_email(data.email):
        return jsonify({"success": False, "message": "Email already registered"}), 409

    # name is optional in the schema
    user = UserService.create_user(data.email, data.password, getattr(data, "name", None))
    return jsonify({"success": True, "message": "User registered", "user_id": user.id}), 201


@auth_bp.post("/login")
def login():
    try:
        data = UserLoginSchema(**request.json)
    except ValidationError as e:
        return jsonify({"success": False, "error": e.errors()}), 400

    user = UserService.get_by_email(data.email)
    if not user or not user.check_password(data.password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({"success": True, "message": "Login successful"})
    set_access_cookies(response, access_token)

    UserService.update_last_login(user)

    return response, 200


@auth_bp.post("/logout")
def logout():
    response = jsonify({"success": True, "message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/google", methods=["GET"])
def google_login():
    """
    Start Google OAuth Code flow. Prefer building the redirect_uri dynamically to
    match the current host (prod or dev). Fall back to env var if explicitly set.
    """
    # Prefer dynamic URL to avoid env mismatches between dev/prod
    dynamic_redirect_uri = url_for("auth.google_callback", _external=True)
    redirect_uri = GOOGLE_REDIRECT_URI or dynamic_redirect_uri

    google_oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        "&scope=openid%20email%20profile"
        "&prompt=select_account"
        "&access_type=offline"
    )
    return redirect(google_oauth_url)


@auth_bp.route("/google/callback")
def google_callback():
    try:
        code = request.args.get("code")
        if not code:
            return "Missing Google code", 400

        # Exchange code → tokens
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token as google_id_token
        import requests

        token_url = "https://oauth2.googleapis.com/token"
        # Use the same redirect_uri as used at the authorize step
        dynamic_redirect_uri = url_for("auth.google_callback", _external=True)
        redirect_uri = GOOGLE_REDIRECT_URI or dynamic_redirect_uri

        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(token_url, data=data).json()

        if "id_token" not in token_response:
            return jsonify({"success": False, "msg": "Token exchange failed"}), 400

        id_token_value = token_response["id_token"]

        info = google_id_token.verify_oauth2_token(
            id_token_value,
            Request(),
            GOOGLE_CLIENT_ID
        )

        google_id = info.get("sub")
        email = info.get("email")

        user = UserService.create_or_get_google_user(
            email=email,
            google_id=google_id
        )

        # Generate JWT cookie
        access_token = create_access_token(identity=str(user.id))

        # REDIRECT to dashboard, not return JSON
        resp = redirect(url_for("main.dashboard_page"))
        set_access_cookies(resp, access_token)

        return resp

    except Exception as e:
        print("Google login error:", e)
        return jsonify({"success": False, "msg": str(e)}), 400


# ---------------------------
# Login / Register UI Pages
# ---------------------------

@auth_bp.get("/login")
def login_page():
    return render_template("auth/login.html")


@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")
