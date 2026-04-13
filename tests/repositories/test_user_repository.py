import pytest
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.repositories.user_repository import UserRepository
from app.models.user import User

def test_create_user(db):
    repo = UserRepository(db)

    user = repo.create_user(
        login="john",
        email=EmailStr("john@example.com"),
        hashed_password="hashed123"
    )

    assert user.id is not None
    assert user.login == "john"
    assert user.email == "john@example.com"

    # Verify in DB
    db_user = db.query(User).filter(User.id == user.id).first()
    assert db_user is not None


def test_get_user_by_login(db):
    repo = UserRepository(db)

    repo.create_user(
        login="john",
        email=EmailStr("john@example.com"),
        hashed_password="hashed123"
    )

    user = repo.get_user_by_login("john")

    assert user is not None
    assert user.login == "john"

def test_get_user_by_login_not_found(db):
    repo = UserRepository(db)

    user = repo.get_user_by_login("missing")

    assert user is None


def test_get_user_by_id(db):
    repo = UserRepository(db)

    created = repo.create_user(
        login="john",
        email=EmailStr("john@example.com"),
        hashed_password="hashed123"
    )

    user = repo.get_user_by_id(created.id)

    assert user.id == created.id


def test_create_user_duplicate_login(db):
    repo = UserRepository(db)

    repo.create_user(
        login="john",
        email=EmailStr("john1@example.com"),
        hashed_password="hashed123"
    )

    with pytest.raises(IntegrityError):
        repo.create_user(
            login="john",  # duplicate
            email=EmailStr("john2@example.com"),
            hashed_password="hashed123"
        )


def test_create_user_duplicate_email(db):
    repo = UserRepository(db)

    repo.create_user(
        login="john1",
        email=EmailStr("john@example.com"),
        hashed_password="hashed123"
    )

    with pytest.raises(IntegrityError):
        repo.create_user(
            login="john2",
            email=EmailStr("john@example.com"),  # duplicate
            hashed_password="hashed123"
        )