from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from app.config.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials  # ← HERE is your JWT

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload["user_id"]



def hash_password(password: str) -> str:
    """Hash plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify plain-text password against hashed password."""
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int, expires_minutes: int = 60) -> str:
    """Create a JWT access token with expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"user_id": user_id, "exp": expire}
    token = jwt.encode(payload, get_settings().jwt_secret_key, algorithm=get_settings().jwt_algorithm)
    return token


def decode_access_token(token: str) -> dict | None:
    """Decode a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None