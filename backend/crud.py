from typing import Any, Optional
import datetime
from sqlmodel import Session, select
from backend.core.security import get_password_hash, verify_password
from backend.schemas.user import UserCreateSchema
from backend.schemas.prediction import PredictionCreateSchema
from backend.models import User, Prediction
from backend.core.config import settings
from typing import List

RQ_JOB_FINISHED_STATUS = "finished"
RQ_JOB_FAILED_STATUS = "failed"


def create_user(session: Session, user_create: UserCreateSchema) -> User:
    db_obj = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_predictions(session: Session, user_id: int) -> List[Prediction]:
    statement = select(Prediction).where(Prediction.user_id == user_id)
    objects = session.exec(statement)
    return objects


def create_prediction_item(
    session: Session,
    user_id: int,
    rq_job_id: str,
    rq_status: str,
    prediction_input: PredictionCreateSchema,
) -> Prediction:
    current_timestamp: datetime.datetime = datetime.datetime.now()
    db_obj = Prediction.model_validate(
        prediction_input,
        update={
            "user_id": user_id,
            "started_at": current_timestamp,
            "rq_job_id": rq_job_id,
            "rq_status": rq_status,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_prediction_by_id(session: Session, pred_id: int) -> None:
    predicton = session.get(Prediction, pred_id)
    session.delete(predicton)
    session.commit()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(session: Session, email: str, password: str) -> Optional[User]:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
