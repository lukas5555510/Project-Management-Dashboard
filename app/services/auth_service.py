from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import UserService
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def register(self, payload: UserCreate) -> Token:
        if payload.password != payload.repeat_password:
            raise ValueError("Passwords do not match")

        existing_user = self.user_service.get_by_login(payload.login)
        if existing_user:
            raise ValueError("User already exists")

        hashed = hash_password(payload.password)
        user = self.user_service.create_user(payload.login, hashed)

        token = create_access_token(str(user.id))
        return {"access_token": token, "token_type": "bearer"}

    def login(self, payload: UserLogin) -> Token | None:
        user = self.user_service.get_by_login(payload.login)
        if not user or not verify_password(payload.password, user.hashed_password):
            return None
        token = create_access_token(str(user.id))
        return {"access_token": token, "token_type": "bearer"}