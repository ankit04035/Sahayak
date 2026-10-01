"""Authentication routes for registration and login."""

import hashlib
import secrets
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.exceptions import AppException
from backend.app.models.user import User
from backend.app.schemas.user import UserRead

router = APIRouter(tags=["Authentication"])


class RegisterRequest(BaseModel):
    """Registration payload."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseModel):
    """Authentication response payload."""

    message: str
    user: UserRead

    model_config = ConfigDict(from_attributes=True)


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"pbkdf2_sha256$200000${salt}${digest.hex()}"


def _verify_password(password: str, password_hash: str) -> bool:
    if not password_hash or not password_hash.startswith("pbkdf2_sha256$"):
        return False
    try:
        algorithm, iterations, salt, expected_hex = password_hash.split("$", 3)
        iterations_int = int(iterations)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations_int,
        )
        return digest.hex() == expected_hex and algorithm == "pbkdf2_sha256"
    except (ValueError, TypeError):
        return False


@router.post(
    "/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a user account and stores a hashed password in the database.",
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    normalized_email = str(payload.email).strip().lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise AppException(
            message="An account with this email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="EMAIL_ALREADY_EXISTS",
        )

    user = User(
        name=payload.name.strip(),
        email=normalized_email,
        password_hash=_hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Account created successfully.", "user": UserRead.model_validate(user)}


@router.post(
    "/auth/login",
    response_model=AuthResponse,
    summary="Verify login credentials",
    description="Checks the supplied email and password, then returns the authenticated user profile.",
)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    normalized_email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise AppException(
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
        )

    return {"message": "Login successful.", "user": UserRead.model_validate(user)}
