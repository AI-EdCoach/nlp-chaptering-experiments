import os
from typing import Any, List
from pydantic import DirectoryPath
from fastapi import APIRouter, Depends, HTTPException
from backend.api.v1.dependencies import (
    SessionDep,
    CurrentUserDep,
)
from backend.schemas.videos import NewVideoSchema
from backend.const import UPLOADED_VIDEOS_ROOT

VIDEO_NAME_ZERO_PADDING_LEN = 6

router = APIRouter()


@router.get("/new", response_model=NewVideoSchema)
def get_name_for_new_video() -> Any:
    """
    Get suitable name for the new video.
    """
    existing_videos_names_numeric_repr: List[int] = [
        int(os.path.splitext(filename)[0])
        for filename in os.listdir(UPLOADED_VIDEOS_ROOT)
    ]
    max_number_name: int = 0
    if existing_videos_names_numeric_repr:
        max_number_name = max(existing_videos_names_numeric_repr)

    new_video_name = f"{max_number_name + 1:06d}"
    return NewVideoSchema(name=new_video_name)
