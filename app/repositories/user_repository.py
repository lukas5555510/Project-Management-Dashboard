from fastapi import Depends
from pydantic import EmailStr

from app.db.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_user(self, login: str, email: EmailStr, hashed_password: str) -> User:
        """
        Create and persist a new user in the database.

        :param login: Unique username for the user
        :param email: Valid email address of the user
        :param hashed_password: Pre-hashed password string
        :return: The newly created User object
        """

        obj = User(
            login=login,
            email=email,
            hashed_password=hashed_password
        )

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def get_user_by_login(self, login: str) -> User:
        """
        Retrieve a user by their login (username).

        :param login: Username to search for
        :return: User object if found, otherwise None
        """

        return self.db.query(User).filter(User.login == login).first()


    def get_user_by_id(self, user_id: int) -> User:
        """
        Retrieve a user by their unique ID.

        :param user_id: Unique identifier of the user
        :return: User object if found, otherwise None
        """

        return self.db.query(User).filter(User.id == user_id).first()