from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials  # ← HERE is your JWT

    try:
        payload = decode_access_token(token)
        return payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_current_user(
    token: str,
    user_service: UserService = Depends(get_user_service),
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = user_service.get_by_id(payload["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user