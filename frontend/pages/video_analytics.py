import base64
import dash
from dash import dash_table
import dash_player as dp
from pathlib import Path
from http import HTTPStatus
from pydantic import FilePath
from requests import Response
from datetime import date, datetime
from dash import Dash, html, dcc, Input, Output, callback, State, ctx, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from typing import List, Optional, Tuple, Dict
from backend.schemas.prediction import TimeCodes, Chapter
from frontend.api_utils import (
    get_name_for_new_video,
    init_timecode_predict,
    get_timecode_prediction,
)
from frontend.const import STATIC_FRONTEND_DIR, ALLOWED_VIDEO_EXTENSIONS
import cv2
import pandas as pd

PLAYER_PXL_LENGTH = 640
SPACING_PIXELS = 3
TIMECODES_HEIGHT = 15
dash.register_page(__name__)


def timecodes_to_dataframe(timecodes: TimeCodes) -> pd.DataFrame:
    data = []
    columns = [
        "title",
        "start",
        "end",
        "content",
    ]
    for chapter in timecodes.chapters:
        data.append([chapter.title, chapter.start, chapter.end, chapter.content])
    dframe = pd.DataFrame(data, columns=columns)
    return dframe


def get_video_len_in_seconds(video_path: FilePath) -> int:
    cap = cv2.VideoCapture(str(video_path))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    length_seconds = int(frame_count / fps)
    return length_seconds


def seconds2pixels(len_pixels, len_seconds, seconds_num: int) -> int:
    percentage = seconds_num / len_seconds
    return int(percentage * len_pixels)


def create_timecodes_chapters_buttons(
    timecodes: TimeCodes, global_length_pixels: int, video_length_seconds: int
) -> List[html.Button]:
    chapters: List[Chapter] = sorted(
        timecodes.chapters, key=lambda chapter: chapter.start
    )
    buttons: List[html.Button] = []
    chapter: Chapter
    compensate_spacing = 0
    effective_pxl_length = global_length_pixels - SPACING_PIXELS * (len(chapters) - 1)

    summary_width = 0
    for chapter_index, chapter in enumerate(chapters):
        width_pixels = seconds2pixels(
            len_pixels=effective_pxl_length,
            len_seconds=video_length_seconds,
            seconds_num=chapter.end - chapter.start,
        )
        summary_width += chapter_index
        offset_from_last_pixels = 0
        if chapter_index > 0:
            offset_from_last_pixels: int = seconds2pixels(
                len_pixels=effective_pxl_length,
                len_seconds=video_length_seconds,
                seconds_num=chapter.start - chapters[chapter_index - 1].end,
            )
        current_offset_from_last = max(offset_from_last_pixels, SPACING_PIXELS)
        button_offset = current_offset_from_last + compensate_spacing
        button = html.Button(
            "",
            id={"type": "btn-nclicks", "index": chapter_index},
            n_clicks=0,
            style={
                "height": f"{TIMECODES_HEIGHT}px",
                "width": f"{width_pixels}px",
                "position": "relative",
                "top": "0px",
                "left": f"{button_offset}px",
            },
            className="hoverable_button",
        )
        compensate_spacing += current_offset_from_last
        buttons.append(button)
    return buttons


@callback(
    Output("chapter_headline", "children"),
    Output("chapter_text", "children"),
    Input({"type": "btn-nclicks", "index": ALL}, "n_clicks"),
    State("timecodes_session", "data"),
)
def show_chapter_header(n_clicks, session_data):
    button_index = -1
    if ctx.triggered_id is not None:
        button_index = ctx.triggered_id["index"]
    if button_index == -1:
        return "", ""
    timecodes: TimeCodes = TimeCodes.model_validate(session_data["timecodes"])
    chapter: Chapter = timecodes.chapters[button_index]
    return chapter.title, chapter.content


@callback(
    Output("player", "seekTo"),
    Input({"type": "btn-nclicks", "index": ALL}, "n_clicks"),
    State("timecodes_session", "data"),
)
def trigger_chapter_play(n_clicks, session_data):
    button_index = -1
    if ctx.triggered_id is not None:
        button_index = ctx.triggered_id["index"]
    if button_index == -1:
        return 0
    timecodes: TimeCodes = TimeCodes.model_validate(session_data["timecodes"])
    return timecodes.chapters[button_index].start


def write_video_from_contents(contents, output_path: FilePath) -> None:
    _, content_string = contents.split(",")
    fh = open(output_path, "wb")
    fh.write(base64.b64decode(content_string))
    fh.close()


@callback(
    Output("uploaded_video_session", "data"),
    Output("uploaded_video_info", "children"),
    Output("incorrect_input_file", "is_open"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
    State("uploaded_video_session", "data"),
)
def updload_video_callback(
    content: str, filename: str, session_data
) -> Tuple[List, bool]:
    should_trigger_filetype_alert: bool = False
    if content is None:
        return session_data, [], should_trigger_filetype_alert

    filename_suffix = Path(filename).suffix
    if filename_suffix not in ALLOWED_VIDEO_EXTENSIONS:
        should_trigger_filetype_alert = True
        return session_data, [], should_trigger_filetype_alert

    new_video_name = get_name_for_new_video()
    output_path = STATIC_FRONTEND_DIR / f"{new_video_name}{filename_suffix}"
    write_video_from_contents(contents=content, output_path=output_path)
    children = [
        html.H2(
            f"You have uploaded video {filename}",
            style={"margin-left": "2%", "margin-top": "2%"},
        ),
        dp.DashPlayer(
            id="player",
            url=str(output_path.relative_to(STATIC_FRONTEND_DIR.parent)),
            controls=True,
            width=PLAYER_PXL_LENGTH,
            style={"margin-left": "2%", "margin-top": "2%"},
        ),
    ]
    session_data["video_name"] = output_path.name
    return session_data, children, should_trigger_filetype_alert


@callback(
    Output("timecodes_session", "data"),
    Output("timecode_output", "children"),
    Input("rand_forest_button", "n_clicks"),
    State("uploaded_video_session", "data"),
    State("login_session", "data"),
    State("timecodes_session", "data"),
)
def timecode_analysis_trigger_callback(
    n_clicks: int, uploaded_video_session, login_session, timecodes_session
):
    if n_clicks is None:
        raise PreventUpdate
    if n_clicks <= 0:
        return

    token = login_session["token"]
    video_name = uploaded_video_session["video_name"]
    response = init_timecode_predict(token=token, video_name=video_name)
    timecode_job_id = response.json()["id"]
    timecodes: TimeCodes = get_timecode_prediction(
        token=token, prediction_id=timecode_job_id
    )
    dataframe_repr: pd.DataFrame = timecodes_to_dataframe(timecodes)

    timecodes_session["timecodes"] = timecodes.model_dump()
    video_path: FilePath = STATIC_FRONTEND_DIR / video_name
    video_length_seconds = get_video_len_in_seconds(video_path)
    buttons = create_timecodes_chapters_buttons(
        timecodes=timecodes,
        global_length_pixels=550,
        video_length_seconds=video_length_seconds,
    )
    return timecodes_session, [
        dp.DashPlayer(
            id="player",
            url=str(video_path.relative_to(STATIC_FRONTEND_DIR.parent)),
            controls=True,
            width=PLAYER_PXL_LENGTH,
            style={"margin-left": "2%", "margin-top": "2%"},
        ),
        html.Div(buttons, style={"margin-left": "2%"}),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            id="chapter_headline",
                            children="",
                            style={
                                "width": f"{PLAYER_PXL_LENGTH}px",
                                "margin-left": "2%",
                                "margin-top": "2%",
                            },
                            className="tset-css",
                        ),
                        html.H5(
                            id="chapter_text",
                            children="text",
                            style={
                                "width": f"{PLAYER_PXL_LENGTH}px",
                                "margin-left": "2%",
                                "margin-top": "2%",
                            },
                        ),
                    ]
                ),
            ],
            style={"position": "relative", "top": "20px"},
        ),
        dbc.Button(
            "Download as csv",
            id="download_as_csv",
            style={"margin-left": "2%", "margin-top": "2%"},
        ),
    ]


def layout():
    layout = html.Div(
        [
            dbc.Alert(
                f"Incorrect extension, should be one of {ALLOWED_VIDEO_EXTENSIONS}",
                color="danger",
                id="incorrect_input_file",
                is_open=False,
                duration=5000,
            ),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Upload Video"]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,
            ),
            html.Div(id="uploaded_video_info", children=[]),
            html.H2(
                "Timecode Analysis",
                style={"margin-left": "2%", "margin-top": "2%"},
            ),
            dbc.Button(
                "Predict",
                id="rand_forest_button",
                style={"margin-left": "2%", "margin-top": "2%"},
            ),
            dcc.Loading(
                id="timecode_loaders",
                type="default",
                children=html.Div(id="timecode_output", children=[]),
            ),
        ]
    )
    return layout
