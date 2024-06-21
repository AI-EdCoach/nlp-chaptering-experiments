from pydantic import FilePath
from typing import Any
import pandas as pd
import pickle
from backend.schemas.prediction import TimeCodes, Chapter
from backend.const import UPLOADED_VIDEOS_ROOT
from typing import Dict, Protocol, Optional
from timecodes import sp2txt, sp2chptrs, chptrs2timecodes


def resolve_full_path_to_video(video_name: str) -> FilePath:
    full_path = UPLOADED_VIDEOS_ROOT / video_name
    return full_path


def timecode_prediction(video_name: str) -> TimeCodes:
    import time

    time.sleep(10)
    video_fullpath: FilePath = resolve_full_path_to_video(video_name)
    print(f"RUNNING ON {video_fullpath}")
    res = sp2txt(video_fullpath)
    timecodes = chptrs2timecodes.call_for_segments(res, summarize=True)
    output = TimeCodes.model_validate(timecodes)
    return output
