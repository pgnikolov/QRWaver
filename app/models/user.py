from datetime import datetime, UTC
from app.extensions.extensions import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

    google_id = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime(timezone=True))

    # -----------------------------------
    # PASSWORDS
    # -----------------------------------
    def set_password(self, password: str):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return pbkdf2_sha256.verify(password, self.password_hash)
