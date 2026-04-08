from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify plain-text password against hashed password."""
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int, expires_minutes: int = 60) -> str:
    """Create a JWT access token with expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"user_id": str(user_id), "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None

def get_user_id_from_token(token: str) -> int | None:
    """Get user id from JWT token."""

    payload = decode_access_token(token)
    if payload:
        return payload["user_id"]
    return None