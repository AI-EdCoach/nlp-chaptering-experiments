from http import HTTPStatus
from sqlmodel import Session
from backend.models import User
from fastapi.testclient import TestClient
from .utils import client_fixture, session_fixture
from sqlmodel import Session
from backend.core.config import settings
from backend.core.security import get_password_hash

USERS_ENDPOINT = f"{settings.API_V1_STR}/users"
LOGIN_ENDPOINT = f"{settings.API_V1_STR}/auth/login"
TEST_EMAIL = "test_email.one@gmail.com"
TEST_PWD = "password123456"
TEST_PWD_HASH = get_password_hash(TEST_PWD)

TEST_DATABASE_USER = User(
    name="test",
    email=TEST_EMAIL,
    hashed_password=TEST_PWD_HASH,
    is_active=True,
    is_superuser=False,
)


def add_user(session: Session) -> None:
    session.add(TEST_DATABASE_USER)
    session.commit()


def test_users_me(client_fixture: TestClient, session_fixture: Session):
    add_user(session_fixture)
    login_response = client_fixture.post(
        LOGIN_ENDPOINT, data={"username": TEST_EMAIL, "password": TEST_PWD}
    )
    login_repsponse_data = login_response.json()
    assert login_response.status_code == HTTPStatus.OK

    access_token = login_repsponse_data["access_token"]
    users_me_response = client_fixture.get(
        f"{USERS_ENDPOINT}/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = users_me_response.json()
    assert users_me_response.status_code == HTTPStatus.OK
    assert user_data["name"] == TEST_DATABASE_USER.name
    assert user_data["email"] == TEST_DATABASE_USER.email
    assert user_data["is_active"] == TEST_DATABASE_USER.is_active
    assert user_data["is_superuser"] == TEST_DATABASE_USER.is_superuser
