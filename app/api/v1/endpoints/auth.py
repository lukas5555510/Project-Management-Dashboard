from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, Token, UserResponse, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/auth", response_model=Token)
def create_user(user: UserCreate, auth_service: AuthService = Depends()):
    return auth_service.register(user)


@router.post("/login", response_model=Token)
def login(user: UserLogin, auth_service: AuthService = Depends()):
    return auth_service.login(user)
