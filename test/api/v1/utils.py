import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from backend.models import User, Prediction
from backend.main import app
from backend.api.v1.dependencies import SessionDep, get_db


@pytest.fixture(name="session_fixture")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client_fixture")
def client_fixture(session_fixture: Session):
    def get_session_override():
        return session_fixture

    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
