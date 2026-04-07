from app.core.security import pwd_context, create_access_token, decode_access_token
from app.repositories.user_repository import UserRepository
from app.config.settings import settings
from fastapi import HTTPException

class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    def create_user(self, login: str, email: str, password: str, repeat_password: str):
        if password != repeat_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        if self.repo.get_user_by_login(login):
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = pwd_context.hash(password)

        return self.repo.create_user(login, email, hashed_password)

    def authenticate_user(self, login: str, password: str):
        user = self.repo.get_user_by_login(login)

        if not user or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user

    def login(self, login: str, password: str):
        user = self.authenticate_user(login, password)

        token = create_access_token(user.login,settings.expires_minutes)

        return {
            "access_token": token,
            "token_type": "bearer"
        }