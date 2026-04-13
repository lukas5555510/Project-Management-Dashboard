from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseRequestError
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from fastapi import Depends


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = UserRepository(db)


    def create_user(self, login: str, email: EmailStr, hashed_password: str) -> User:
        """
        Create a new user in the system.

        This method delegates user creation to the repository layer and persists
        the user in the database.

        :param login: Unique login of the user
        :param email: Valid email address of the user
        :param hashed_password: Pre-hashed password string
        :return: The created User object
        :raises DatabaseRequestError: If a database error occurs during creation
        """

        try:
            return self.repo.create_user(login, email, hashed_password)
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error creating user")


    def get_user_by_login(self, login: str) -> User:
        """
        Retrieve a user by their login.

        This method queries the database for a user matching the given login.

        :param login: login of the user to retrieve
        :return: User object if found
        :raises DatabaseRequestError: If a database error occurs during lookup
        """

        try:
            return self.repo.get_user_by_login(login)
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error checking user by login")


    def get_user_by_id(self, user_id: int) -> User:
        """
        Retrieve a user by their unique ID.

        This method fetches a user record from the database using the user's ID.

        :param user_id: Unique identifier of the user
        :return: User object if found
        :raises DatabaseRequestError: If a database error occurs during lookup
        """
        try:
            return self.repo.get_user_by_id(user_id)
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error checking user by id")
