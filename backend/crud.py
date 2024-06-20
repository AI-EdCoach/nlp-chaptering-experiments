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
    model_id: int,
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


def update_prediction_after_successfull_finish(
    session: Session, prediction_id: int, result: str
) -> Prediction:
    db_prediction: Prediction = session.get(Prediction, prediction_id)
    if db_prediction.rq_status == RQ_JOB_FINISHED_STATUS:
        return db_prediction

    db_prediction.rq_status = RQ_JOB_FINISHED_STATUS
    db_prediction.result = result
    session.add(db_prediction)
    session.commit()
    session.refresh(db_prediction)
    return db_prediction


def update_prediction_after_fail(session: Session, prediction_id: int) -> None:
    db_prediction: Prediction = session.get(Prediction, prediction_id)
    if db_prediction.rq_status == RQ_JOB_FINISHED_STATUS:
        return db_prediction

    db_prediction.rq_status = RQ_JOB_FAILED_STATUS
    session.add(db_prediction)
    session.commit()
    session.refresh(db_prediction)
    return db_prediction


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
