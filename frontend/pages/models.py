import base64
import dash
import dash_player as dp
from pathlib import Path
from http import HTTPStatus
from pydantic import FilePath
from requests import Response
from datetime import date, datetime
from dash import Dash, html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from typing import List, Optional, Tuple, Dict
from frontend.api_utils import (
    wait_untill_prediction_end,
    init_predict,
    get_current_user_data_via_api,
    get_name_for_new_video,
)
from frontend.const import STATIC_FRONTEND_DIR, ALLOWED_VIDEO_EXTENSIONS

PLAYER_PXL_LENGTH = 640
dash.register_page(__name__)


def write_video_from_contents(contents, output_path: FilePath) -> None:
    _, content_string = contents.split(",")
    fh = open(output_path, "wb")
    fh.write(base64.b64decode(content_string))
    fh.close()


@callback(
    Output("uploaded_video_info", "children"),
    Output("incorrect_input_file", "is_open"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
)
def update_output(content: str, filename: str) -> Tuple[List, bool]:
    should_trigger_filetype_alert: bool = False
    if content is None:
        return [], should_trigger_filetype_alert

    filename_suffix = Path(filename).suffix
    if filename_suffix not in ALLOWED_VIDEO_EXTENSIONS:
        should_trigger_filetype_alert = True
        return [], should_trigger_filetype_alert

    new_video_name = get_name_for_new_video()
    output_path = STATIC_FRONTEND_DIR / f"{new_video_name}{filename_suffix}"
    write_video_from_contents(contents=content, output_path=output_path)
    children = [
        html.H2(f"You have uploaded video {filename}"),
        dp.DashPlayer(
            id="player",
            url=str(output_path.relative_to(STATIC_FRONTEND_DIR.parent)),
            controls=True,
            width=PLAYER_PXL_LENGTH,
        ),
    ]
    return children, should_trigger_filetype_alert


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
                children=html.Div(
                    ["Upload Video. Drag and Drop ", html.A("Select Files")]
                ),
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
        ]
    )
    return layout
