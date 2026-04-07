from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/auth", response_model=UserCreate)
async def create_user(user: UserCreate, auth_service: AuthService = Depends()):
    return await auth_service.register(user)

@router.post("/login")
async def login(user: UserLogin, auth_service: AuthService = Depends()):
    return await auth_service.login(user)