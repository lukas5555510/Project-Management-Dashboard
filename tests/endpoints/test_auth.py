import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.services.auth_service import AuthService


@pytest.fixture
def mock_auth_service():
    return MagicMock(spec=AuthService)


@pytest.fixture
def client(mock_auth_service):
    app.dependency_overrides[AuthService] = lambda: mock_auth_service
    return TestClient(app)

class TestAuthEndpoints:
    # -------------------------
    # REGISTER (/auth)
    # -------------------------

    def test_register_success(self,client, mock_auth_service):
        request_payload = {
            "login": "john",
            "email": "john@example.com",
            "password": "secret123",
            "repeat_password": "secret123"
        }

        service_response = {
            "access_token": "jwt-token",
            "token_type": "bearer"
        }

        mock_auth_service.register.return_value = service_response

        response = client.post("/auth", json=request_payload)

        assert response.status_code == 201
        assert response.json() == service_response

        mock_auth_service.register.assert_called_once()

# for all endpoints both happy and sad scenario
# fix the bug we found
    def test_register_password_mismatch(self,client, mock_auth_service):
        from fastapi import HTTPException

        request_payload = {
            "login": "john",
            "email": "john@example.com",
            "password": "secret123",
            "repeat_password": "different"
        }

        mock_auth_service.register.side_effect = HTTPException(
            status_code=401,
            detail="Passwords do not match"
        )

        response = client.post("/auth", json=request_payload)

        assert response.status_code == 401
        assert response.json()['detail'] == "Passwords do not match"


    def test_register_validation_error_missing_fields(self,client):
        # missing password fields → Pydantic validation
        response = client.post("/auth", json={
            "login": "john",
            "email": "john@example.com"
        })

        assert response.status_code == 422


    # -------------------------
    # LOGIN (/login)
    # -------------------------

    def test_login_success(self,client, mock_auth_service):
        request_payload = {
            "login": "john",
            "password": "secret123"
        }

        service_response = {
            "access_token": "jwt-token",
            "token_type": "bearer"
        }

        mock_auth_service.login.return_value = service_response

        response = client.post("/login", json=request_payload)

        assert response.status_code == 200
        assert response.json() == service_response

        mock_auth_service.login.assert_called_once()


    def test_login_invalid_credentials(self,client, mock_auth_service):
        from fastapi import HTTPException

        request_payload = {
            "login": "john",
            "password": "wrong-password"
        }

        mock_auth_service.login.side_effect = HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

        response = client.post("/login", json=request_payload)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"


    def test_login_validation_error_missing_password(self,client):
        response = client.post("/login", json={
            "login": "john"
        })

        assert response.status_code == 422