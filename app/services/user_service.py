from datetime import datetime, UTC
from app.extensions.extensions import db
from app.models.user import User


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
