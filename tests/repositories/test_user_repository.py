import pytest
from unittest.mock import MagicMock

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.project import ProjectUser, Project
from app.models.document import Document


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user_repo(mock_db):
    return UserRepository(db=mock_db)

class TestUserRepository:
    # -------------------------
    # CREATE USER
    # -------------------------

    def test_create_user_success(self,user_repo, mock_db):
        # given
        login = "john"
        email = "john@example.com"
        hashed_password = "hashed123"

        # when
        result = user_repo.create_user(login, email, hashed_password)

        # then
        # check object created correctly
        assert isinstance(result, User)
        assert result.login == login
        assert result.email == email
        assert result.hashed_password == hashed_password

        # verify DB interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(result)


    # -------------------------
    # GET USER BY LOGIN
    # -------------------------

    def test_get_user_by_login_found(self,user_repo, mock_db):
        # given
        login = "john"

        expected_user = User(id=1, login=login, email="john@example.com", hashed_password="x")

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = expected_user

        # when
        result = user_repo.get_user_by_login(login)

        # then
        assert result == expected_user

        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()


    def test_get_user_by_login_not_found(self,user_repo, mock_db):
        # given
        login = "unknown"

        mock_db.query.return_value.filter.return_value.first.return_value = None

        # when
        result = user_repo.get_user_by_login(login)

        # then
        assert result is None


    # -------------------------
    # GET USER BY ID
    # -------------------------

    def test_get_user_by_id_found(self,user_repo, mock_db):
        # given
        user_id = 1
        expected_user = User(id=user_id, login="john", email="john@example.com", hashed_password="x")

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = expected_user

        # when
        result = user_repo.get_user_by_id(user_id)

        # then
        assert result == expected_user

        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()


    def test_get_user_by_id_not_found(self,user_repo, mock_db):
        # given
        user_id = 999
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # when
        result = user_repo.get_user_by_id(user_id)

        # then
        assert result is None