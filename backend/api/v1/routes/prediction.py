import os
from dotenv import load_dotenv
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
from worker import timecode_prediction
from backend.models import Prediction
from backend.schemas.prediction import (
    PredictionCreateSchema,
    PreductionCreationOutput,
    TimeCodes,
    TimeCodePredictionOutput,
)
from backend.crud import create_prediction_item, delete_prediction_by_id

load_dotenv()
redis_conn = Redis(host="project_redis", port=os.environ["REDIS_PORT"])
queue = Queue(connection=redis_conn)
RQ_JOB_FINISHED_STATUS = "finished"
RQ_JOB_FAILED_STATUS = "failed"

EMPTY_TIMECODES = TimeCodePredictionOutput(timecodes=None, rq_status=None)
router = APIRouter()


@router.get("/timecode/{prediction_id}", response_model=TimeCodePredictionOutput)
def get_timecodes_result(
    prediction_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    prediction: Optional[Prediction] = session.get(Prediction, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Invalid prediction id")
    if prediction.user_id != current_user.id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail="Users are allowed to see only their predictions",
        )

    rq_job: RqJob = RqJob.fetch(prediction.rq_job_id, connection=redis_conn)
    rq_job_status = rq_job.get_status()
    rq_based_output: TimeCodePredictionOutput = TimeCodePredictionOutput(
        timecodes=None, rq_status=rq_job_status
    )
    if rq_job_status == RQ_JOB_FINISHED_STATUS:
        delete_prediction_by_id(
            session=session,
            pred_id=prediction_id,
        )
        rq_based_output.timecodes = rq_job.result
    if rq_job_status == RQ_JOB_FAILED_STATUS:
        delete_prediction_by_id(
            session=session,
            pred_id=prediction_id,
        )
    return rq_based_output


@router.post("/timecode/", response_model=PreductionCreationOutput)
def start_timecode_prediction(
    session: SessionDep,
    current_user: CurrentUserDep,
    prediction_create_input: PredictionCreateSchema,
) -> Any:
    """
    Start timecode prediction.
    """
    rq_job = queue.enqueue(timecode_prediction, prediction_create_input.video_name)
    created_prediction = create_prediction_item(
        session=session,
        user_id=current_user.id,
        prediction_input=prediction_create_input,
        rq_job_id=rq_job.id,
        rq_status=rq_job.get_status(),
    )
    return created_prediction
