from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class UserRegisterSchema(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str

    @validator("password")
    def password_policy(cls, v: str):
        # Min 8 chars, at least 1 letter, 1 number, 1 special symbol
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
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
