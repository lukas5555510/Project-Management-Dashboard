from fastapi import APIRouter, Depends

from app.api.deps import get_user_service
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter()
# use JWT authorization important
@router.post("/auth", response_model=UserCreate)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    created_user = service.create_user(
        login=user.login,
        email=user.email,
        password=user.password,
        repeat_password=user.repeat_password
    )

    return {
        "id": created_user.id,
        "login": created_user.login,
        "email": created_user.email
    }


@router.post("/login")
def login(
    user: UserLogin,
    service: UserService = Depends(get_user_service)
):
    return service.login(
        login=user.login,
        password=user.password
    )