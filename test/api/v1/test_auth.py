from http import HTTPStatus
from sqlmodel import Session
from backend.models import User
from fastapi.testclient import TestClient
from .utils import client_fixture, session_fixture
from sqlmodel import Session
from backend.core.config import settings
from backend.core.security import get_password_hash

REGISTER_ENDPOINT = f"{settings.API_V1_STR}/auth/register"
LOGIN_ENDPOINT = f"{settings.API_V1_STR}/auth/login"
TEST_EMAIL = "test_email.one@gmail.com"
TEST_PWD = "password123456"
TEST_PWD_HASH = get_password_hash(TEST_PWD)


def test_register(client_fixture: TestClient) -> None:
    response = client_fixture.post(
        REGISTER_ENDPOINT,
        json={
            "name": "test_name",
            "email": TEST_EMAIL,
            "is_active": True,
            "is_superuser": False,
            "password": TEST_PWD,
        },
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data["name"] == "test_name"
    assert data["email"] == TEST_EMAIL
    assert data["is_active"] is True
    assert data["is_superuser"] is False


def test_register_with_existing_email(
    client_fixture: TestClient, session_fixture: Session
):
    db_obj = User(
        name="test",
        email=TEST_EMAIL,
        hashed_password=TEST_PWD_HASH,
        is_active=True,
        is_superuser=False,
    )
    session_fixture.add(db_obj)
    session_fixture.commit()

    response = client_fixture.post(
        REGISTER_ENDPOINT,
        json={
            "name": "test_name",
            "email": TEST_EMAIL,
            "is_active": False,
            "is_superuser": False,
            "password": "pwd",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_with_correct_credentials(
    client_fixture: TestClient, session_fixture: Session
) -> None:
    db_obj = User(
        name="test",
        email=TEST_EMAIL,
        hashed_password=TEST_PWD_HASH,
        balance=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    session_fixture.add(db_obj)
    session_fixture.commit()

    response = client_fixture.post(
        LOGIN_ENDPOINT, data={"username": TEST_EMAIL, "password": TEST_PWD}
    )
    assert response.status_code == HTTPStatus.OK


def test_failed_login_with_incorrect_credentials(
    client_fixture: TestClient, session_fixture: Session
) -> None:
    db_obj = User(
        name="test",
        email=TEST_EMAIL,
        hashed_password=TEST_PWD_HASH,
    )
    session_fixture.add(db_obj)
    session_fixture.commit()

    response = client_fixture.post(
        LOGIN_ENDPOINT, data={"username": TEST_EMAIL, "password": "wrong_password"}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_failed_login_with_correct_credentials_for_inactive_user(
    client_fixture: TestClient, session_fixture: Session
) -> None:
    db_obj = User(
        name="test",
        email=TEST_EMAIL,
        hashed_password=TEST_PWD_HASH,
        is_active=False,
    )
    session_fixture.add(db_obj)
    session_fixture.commit()

    response = client_fixture.post(
        LOGIN_ENDPOINT, data={"username": TEST_EMAIL, "password": TEST_PWD}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
