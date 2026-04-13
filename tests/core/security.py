import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import security

class FakeSettings:
    jwt_secret_key = "secret"
    jwt_algorithm = "HS256"


class TestSecurity:

    @patch("app.core.security.get_settings", return_value=FakeSettings())
    def test_create_and_decode_token(self, mock_settings):
        token = security.create_access_token(user_id=123, expires_minutes=10)

        payload = security.decode_access_token(token)

        assert payload is not None
        assert payload["user_id"] == 123
        assert "exp" in payload


    @patch("app.core.security.get_settings", return_value=FakeSettings())
    def test_decode_invalid_token_returns_none(self, mock_settings):
        result = security.decode_access_token("invalid.token")

        assert result is None


    @patch("app.core.security.decode_access_token")
    def test_get_current_user_id_success(self, mock_decode):
        mock_decode.return_value = {"user_id": 1}

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "valid.token"

        user_id = security.get_current_user_id(credentials)

        assert user_id == 1
        mock_decode.assert_called_once_with("valid.token")


    @patch("app.core.security.decode_access_token")
    def test_get_current_user_id_invalid_token(self, mock_decode):
        mock_decode.return_value = None

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "bad.token"

        with pytest.raises(HTTPException) as exc:
            security.get_current_user_id(credentials)

        assert exc.value.status_code == 401
        assert "Invalid token" in exc.value.detail


