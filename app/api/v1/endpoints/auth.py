from fastapi import APIRouter
from app.schemas.user import UserCreate, UserLogin

router = APIRouter()
# use JWT authorization important
@router.post("/auth", response_model=UserCreate)
def create_user(user: UserCreate):
    # implement user creation logic
    return user

@router.post("/login")
def login(user: UserLogin):
    # implement login logic
    return {"message": "Logged in"}