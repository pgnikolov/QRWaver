from datetime import datetime, UTC
from datetime import timedelta
import secrets
import hashlib
from app.extensions.extensions import db
from app.models.user import User
from app.config.settings import PUBLIC_BASE_URL


class UserService:

    @staticmethod
    def create_user(email: str, password: str, name: str | None = None) -> User:
        email = email.strip().lower()
        user = User(email=email)
        if name:
            user.name = name.strip()
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.query.filter_by(email=email.strip().lower()).first()

    @staticmethod
    def update_last_login(user: User):
        user.last_login = datetime.now(UTC)
        db.session.commit()

    @staticmethod
    def create_or_get_google_user(email: str, google_id: str, name: str | None = None) -> User:
        email = email.strip().lower()

        user = User.query.filter_by(email=email).first()

        if user:
            if not user.google_id:
                user.google_id = google_id
                db.session.commit()
            return user

        user = User(
            email=email,
            google_id=google_id,
            password_hash="",
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_google_id(google_id: str):
        return User.query.filter_by(google_id=google_id).first()

    @staticmethod
    def create_google_user(email: str, google_id: str):
        user = User(email=email, google_id=google_id)
        db.session.add(user)
        db.session.commit()
        return user

    # -----------------------------------
    # Email confirmation helpers
    # -----------------------------------
    @staticmethod
    def generate_confirmation_token(user: User, ttl_hours: int = 24) -> str:
        """Generate a confirmation token, store its hash and expiry on the user, and return the raw token.

        We store only the SHA-256 hash in the DB for security; the raw token is returned for emailing.
        """
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        user.confirm_token_hash = token_hash
        user.confirm_expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
        user.confirm_sent_at = datetime.now(UTC)
        db.session.commit()
        return raw_token

    @staticmethod
    def get_by_confirm_token(raw_token: str) -> User | None:
        if not raw_token:
            return None
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        return User.query.filter_by(confirm_token_hash=token_hash).first()

    @staticmethod
    def activate_user(user: User):
        user.is_verified = True
        user.confirm_token_hash = None
        user.confirm_expires_at = None
        db.session.commit()

    @staticmethod
    def can_resend_confirmation(user: User, cooldown_minutes: int = 5) -> bool:
        if not user.confirm_sent_at:
            return True
        delta = datetime.now(UTC) - user.confirm_sent_at
        return delta.total_seconds() >= cooldown_minutes * 60
