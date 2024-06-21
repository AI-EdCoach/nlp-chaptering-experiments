from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PredictionCreateSchema(BaseModel):
    video_name: str


class PreductionCreationOutput(BaseModel):
    id: int


class Chapter(BaseModel):
    """
    A single chapter of text.
    """

    start: int
    end: int
    content: str
    title: Optional[str] = None


class TimeCodes(BaseModel):
    chapters: List[Chapter]


class TimeCodePredictionOutput(BaseModel):
    timecodes: Optional[TimeCodes]
    rq_status: Optional[str]
