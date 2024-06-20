from typing import Optional
from pydantic import FilePath

from typing import List
from datetime import datetime
from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

    predictions: List["Prediction"] = Relationship(back_populates="user_initiator")


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    rq_job_id: str
    rq_status: str
    started_at: datetime
    # prediction output
    user_initiator: User = Relationship(back_populates="predictions")
    video_file: FilePath
