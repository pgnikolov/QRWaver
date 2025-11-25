"""Pydantic schemas for user authentication and registration.

These schemas validate incoming JSON payloads for user registration and login
endpoints. They encapsulate password policy checks and email validation.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class UserRegisterSchema(BaseModel):
    """Schema used to validate the Register request body."""
    name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str

    @validator("password")
    def password_policy(cls, v: str):
        """Enforce a basic password policy.

        Requirements:
        - At least 8 characters
        - Contains at least 1 letter
        - Contains at least 1 number
        - Contains at least 1 special character
        """
        import re
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v: str, values):
        """Ensure the `confirm_password` matches `password`."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLoginSchema(BaseModel):
    """Schema used to validate the Login request body."""
    email: EmailStr
    password: str
