from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from fastapi import HTTPException, Depends


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = UserRepository(db)

    def create_user(self, login: str, email: EmailStr, hashed_password: str):
        return self.repo.create_user(login, email, hashed_password)

    def get_user_by_login(self, login: str) -> User:
        return self.repo.get_user_by_login(login)

    def get_user_by_id(self, user_id: int) -> User:
        return self.repo.get_user_by_id(user_id)

