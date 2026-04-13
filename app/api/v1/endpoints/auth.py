from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, Token, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/auth",
    response_model=Token,
    status_code = 201,
    summary="Register a new user",
    description=(
        "Creates a new user account and returns a JWT access token.\n\n"
        "This endpoint performs user registration by validating input data, "
        "ensuring the user does not already exist, hashing the password, "
        "and issuing an authentication token upon successful creation."
    ),
    responses={
        201: {"detail": "User successfully created and token returned"},
        401: {"detail": "Validation error (e.g., passwords do not match)"},
        409: {"detail": "User already exists"},
    },
)
def create_user(user: UserCreate, auth_service: AuthService = Depends()):
    return auth_service.register(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and return token",
    description=(
        "Authenticates a user using login and password credentials.\n\n"
        "If credentials are valid, returns a JWT access token. "
        "Otherwise, authentication fails with an error."
    ),
    responses={
        200: {"detail": "Successful authentication and token issued"},
        401: {"detail": "Invalid username or password"},
    },
)
def login(user: UserLogin, auth_service: AuthService = Depends()):
    return auth_service.login(user)
