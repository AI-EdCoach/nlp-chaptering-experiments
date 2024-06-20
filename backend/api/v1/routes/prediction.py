from typing import Any, Optional
from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from sqlmodel import delete, func, select
from backend.api.v1.dependencies import SessionDep, CurrentUserDep
from pydantic import BaseModel, ConfigDict
from enum import Enum, auto
from rq import Queue
from rq.job import Job as RqJob
from redis import Redis
from worker import worker_function
from backend.models import Prediction
from backend.schemas.prediction import (
    PredictionCreateSchema,
    PreductionCreationOutput,
    PredictionOutSchema,
)
from backend.crud import (
    create_prediction_item,
    update_prediction_after_fail,
    update_prediction_after_successfull_finish,
)

redis_conn = Redis(host="project_redis", port=6380)
queue = Queue(connection=redis_conn)
RQ_JOB_FINISHED_STATUS = "finished"
RQ_JOB_FAILED_STATUS = "failed"

router = APIRouter()


@router.get("/{prediction_id}", response_model=PredictionOutSchema)
def get_prediction_result(
    prediction_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    print("GET RESULT")
    prediction: Optional[Prediction] = session.get(Prediction, prediction_id)
    print(f"prediction")
    print(prediction)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Invalid prediction id")
    if prediction.user_id != current_user.id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail="Users are allowed to see only their predictions",
        )
    if prediction.rq_status in [RQ_JOB_FINISHED_STATUS, RQ_JOB_FAILED_STATUS]:
        return prediction
    print("job id = ", prediction.rq_job_id)
    rq_job: RqJob = RqJob.fetch(prediction.rq_job_id, connection=redis_conn)
    if rq_job.get_status() == RQ_JOB_FINISHED_STATUS:
        prediction = update_prediction_after_successfull_finish(
            session=session, prediction_id=prediction_id, result=rq_job.result
        )
    if rq_job.get_status() == RQ_JOB_FAILED_STATUS:
        prediction = update_prediction_after_fail(rq_job.result)
    return prediction


@router.post("/{model_name}", response_model=PreductionCreationOutput)
def start_prediction(
    model_name: str,
    session: SessionDep,
    current_user: CurrentUserDep,
    prediction_create_input: PredictionCreateSchema,
) -> Any:
    """
    Retrieve users.
    """
    rq_job = queue.enqueue(worker_function, model_name, prediction_create_input)
    created_prediction = create_prediction_item(
        session=session,
        user_id=current_user.id,
        prediction_input=prediction_create_input,
        rq_job_id=rq_job.id,
        rq_status=rq_job.get_status(),
    )
    return created_prediction
