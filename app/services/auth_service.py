from fastapi import Depends

from app.core.exceptions import ConflictException, InvalidCredentialsError, NotFoundError
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import UserService
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service

    def register(self, payload: UserCreate) -> Token:
        """
        Register a new user and return an authentication token.

        This method handles full user registration flow:
        - Validates that password and repeat_password match
        - Checks if a user with the same login already exists
        - Hashes the user's password
        - Creates a new user in the database
        - Generates an access token for immediate authentication

        :param payload: UserCreate schema containing login, email, password, and repeat_password
        :return: Dictionary containing access token and token type (Bearer)
        :raises InvalidCredentialsError: If passwords do not match
        :raises ConflictException: If a user with the given login already exists
        """
        if payload.password != payload.repeat_password:
            raise InvalidCredentialsError("Passwords do not match")

        existing_user = self.user_service.get_user_by_login(payload.login)
        if existing_user:
            raise ConflictException("User already exists")

        hashed = hash_password(payload.password)
        user = self.user_service.create_user(payload.login, payload.email, hashed)

        token = create_access_token(user.id)
        return {"access_token": token, "token_type": "bearer"}

    def login(self, payload: UserLogin) -> Token:
        """
        Authenticate a user and return an access token.

        This method performs user login by:
        - Retrieving user by login
        - Verifying that the user exists
        - Validating the provided password against the stored hashed password
        - Generating an access token upon successful authentication

        :param payload: UserLogin schema containing login and password
        :return: Dictionary containing access token and token type (Bearer)
        :raises InvalidCredentialsError: If login or password is incorrect
        """

        user = self.user_service.get_user_by_login(payload.login)

        if not user:
            raise InvalidCredentialsError("Wrong username or password")

        if not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError("Wrong username or password")

        token = create_access_token(user.id)
        return {"access_token": token, "token_type": "bearer"}