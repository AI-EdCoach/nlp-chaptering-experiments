from backend.models import User, Prediction
from backend.core.config import settings
from sqlmodel import create_engine, SQLModel, Session, select


engine = create_engine(str(settings.SQLALCHEMY_SQLITE_DATABASE_URI))


def init_db():
    SQLModel.metadata.create_all(engine)
