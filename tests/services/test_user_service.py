import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.services.user_service import UserService
from app.core.exceptions import DatabaseRequestError
from app.models.user import User
from app.models.project import ProjectUser

@pytest.fixture
def service():
    service = UserService()
    service.repo = MagicMock()
    return service

class TestUserService:
    def test_create_user_success(self,service):
        user = MagicMock()
        user.id = 1
        user.login = "john"
        user.email = "john@test.com"
        user.hashed_password = "hashed123"


        service.repo.create_user.return_value = user

        result = service.create_user(
            login="john",
            email="john@test.com",
            hashed_password="hashed123"
        )

        assert result.id == 1
        assert result.login == "john"
        assert result.email == "john@test.com"
        assert result.hashed_password == "hashed123"

        service.repo.create_user.assert_called_once_with(
            "john",
            "john@test.com",
            "hashed123"
        )


    def test_create_user_db_error(self,service):
        service.repo.create_user.side_effect = SQLAlchemyError()

        with pytest.raises(DatabaseRequestError) as exc:
            service.create_user(
                login="john",
                email="john@test.com",
                hashed_password="hashed123"
            )

        assert "Database error creating user" in str(exc.value)


    def test_get_user_by_login_success(self,service):

        user = MagicMock()
        user.id = 2
        user.login = "alice"
        user.email = "alice@test.com"
        user.hashed_password = "hashed456"

        service.repo.get_user_by_login.return_value = user

        result = service.get_user_by_login("alice")

        assert result.id == 2
        assert result.login == "alice"
        assert result.email == "alice@test.com"



    def test_get_user_by_login_db_error(self,service):
        service.repo.get_user_by_login.side_effect = SQLAlchemyError()

        with pytest.raises(DatabaseRequestError):
            service.get_user_by_login("alice")


    def test_get_user_by_id_success(self,service):
        user = MagicMock()
        user.id = 10
        user.login = "bob"
        user.email = "bob@test.com"
        user.hashed_password = "hashed789"

        service.repo.get_user_by_id.return_value = user

        result = service.get_user_by_id(10)

        assert result.id == 10
        assert result.login == "bob"


    def test_get_user_by_id_db_error(self,service):
        service.repo.get_user_by_id.side_effect = SQLAlchemyError()

        with pytest.raises(DatabaseRequestError):
            service.get_user_by_id(10)