from fastapi import Depends
from pydantic import EmailStr

from app.db.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from typing import List


class UserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user(self, login: str, email: EmailStr, hashed_password: str):
        obj = User(
            login=login,
            email=email,
            hashed_password=hashed_password
        )

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def get_user_by_login(self, login: str):
        return self.db.query(User).filter(User.login == login).first()


    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()