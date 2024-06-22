import os
from pydantic import FilePath
from typing import Any
import pandas as pd
import pickle
from backend.schemas.prediction import TimeCodes, Chapter
from backend.const import UPLOADED_VIDEOS_ROOT
from typing import Dict, Protocol, Optional
from timecodes import sp2txt, sp2chptrs, chptrs2timecodes
from timecodes.types import Timecodes as MLTimecodes


def resolve_full_path_to_video(video_name: str) -> FilePath:
    full_path = UPLOADED_VIDEOS_ROOT / video_name
    return full_path


def convert_to_backend_schema(timecodes: MLTimecodes) -> TimeCodes:
    backend_compatible_chapters = []
    for chapter in timecodes.chapters:
        title = " ".join(chapter.content.split(" ")[:5]) + "..."
        backend_compatible_chapters.append(
            Chapter(
                start=int(chapter.start),
                end=int(chapter.end),
                content=chapter.content,
                title=title,
            )
        )
    return TimeCodes(chapters=backend_compatible_chapters)


def timecode_prediction(video_name: str) -> TimeCodes:
    import time

    time.sleep(10)
    video_fullpath: FilePath = resolve_full_path_to_video(video_name)
    res = sp2txt(video_fullpath)
    timecodes = chptrs2timecodes.call_for_segments(res, summarize=True)
    output = convert_to_backend_schema(timecodes)
    return output


def setup():
    print("START SETUP")
    setup_video = "setup_assets/setup_video.mp4"
    print(f"VIDEO EXISTS = {os.path.exists(setup_video)}")
    res = sp2txt(setup_video)
    timecodes = chptrs2timecodes.call_for_segments(res, summarize=True)
    print("TIMECODES")
    print(timecodes.chapters)
    output = convert_to_backend_schema(timecodes)
    print("OUTPUT")
    print(output)


if __name__ == "__main__":
    setup()
