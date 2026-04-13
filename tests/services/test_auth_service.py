import pytest
from unittest.mock import MagicMock, patch

from app.services.auth_service import AuthService
from app.core.exceptions import (
    ConflictException,
    InvalidCredentialsError,
)
from app.schemas.user import UserCreate, UserLogin

@pytest.fixture
def user_service():
    return MagicMock()


@pytest.fixture
def auth_service(user_service):
    return AuthService(user_service=user_service)

class TestAuthService:
    def test_register_password_mismatch(self,auth_service):
        payload = UserCreate(
            login="john",
            email="john@test.com",
            password="123",
            repeat_password="456"
        )

        with pytest.raises(InvalidCredentialsError):
            auth_service.register(payload)

    def test_register_user_exists(self,auth_service, user_service):
        payload = UserCreate(
            login="john",
            email="john@test.com",
            password="123",
            repeat_password="123"
        )

        user_service.get_user_by_login.return_value = MagicMock()

        with pytest.raises(ConflictException):
            auth_service.register(payload)

        user_service.get_user_by_login.assert_called_once_with("john")

    def test_register_success(self,auth_service, user_service):
        payload = UserCreate(
            login="john",
            email="john@test.com",
            password="123",
            repeat_password="123"
        )

        user_service.get_user_by_login.return_value = None

        fake_user = MagicMock()
        fake_user.id = 1
        user_service.create_user.return_value = fake_user

        with patch("app.services.auth_service.hash_password", return_value="hashed_pw") as mock_hash, \
                patch("app.services.auth_service.create_access_token", return_value="token123") as mock_token:
            result = auth_service.register(payload)

        assert result == {
            "access_token": "token123",
            "token_type": "bearer"
        }

        mock_hash.assert_called_once_with("123")
        user_service.create_user.assert_called_once_with(
            "john",
            "john@test.com",
            "hashed_pw"
        )
        mock_token.assert_called_once_with(1)

    def test_login_user_not_found(self,auth_service, user_service):
        payload = UserLogin(login="john", password="123")

        user_service.get_user_by_login.return_value = None

        with pytest.raises(InvalidCredentialsError):
            auth_service.login(payload)

    def test_login_wrong_password(self,auth_service, user_service):
        payload = UserLogin(login="john", password="wrong")

        fake_user = MagicMock()
        fake_user.hashed_password = "hashed_pw"

        user_service.get_user_by_login.return_value = fake_user

        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                auth_service.login(payload)

    def test_login_success(self, auth_service, user_service):
        payload = UserLogin(login="john", password="123")

        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.hashed_password = "hashed_pw"

        user_service.get_user_by_login.return_value = fake_user

        with patch("app.services.auth_service.verify_password", return_value=True), \
                patch("app.services.auth_service.create_access_token", return_value="token123") as mock_token:
            result = auth_service.login(payload)

        assert result == {
            "access_token": "token123",
            "token_type": "bearer"
        }

        mock_token.assert_called_once_with(1)