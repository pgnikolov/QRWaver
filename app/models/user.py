"""Database model for application users.

Defines the `User` SQLAlchemy model, representing registered users, including
fields for email/password as well as optional Google OAuth identifier. The
model provides helper methods for setting and verifying password hashes.
"""

from datetime import datetime, UTC
from app.extensions.extensions import db
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Boolean


class User(db.Model):
    """User account entity.

    Attributes:
        id: Primary key.
        email: Unique email address for the account.
        google_id: Optional Google OAuth subject identifier.
        name: Optional display name.
        password_hash: PBKDF2-SHA256 hash of the password (nullable for SSO).
        created_at: UTC timestamp when the record was created.
        last_login: UTC timestamp of the most recent successful login.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

    google_id = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime(timezone=True))

    # Email verification / activation
    is_verified = db.Column(Boolean, nullable=False, default=False)
    confirm_token_hash = db.Column(db.String(255), nullable=True)
    confirm_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    confirm_sent_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # -----------------------------------
    # Password helpers
    # -----------------------------------
    def set_password(self, password: str):
        """Hash and store the given plaintext password.

        Uses passlib's PBKDF2-SHA256 to derive a secure hash.
        """
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash.

        Returns False if the user has no password set (e.g., SSO-only).
        """
        if not self.password_hash:
            return False
        return pbkdf2_sha256.verify(password, self.password_hash)
