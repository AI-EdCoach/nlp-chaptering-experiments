import dash
from http import HTTPStatus
from requests import Response
from dash import Dash, html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from typing import List, Dict, Tuple
from pprint import pprint
from frontend.api_utils import login_via_api, get_current_user_data_via_api


dash.register_page(__name__)


@callback(
    Output("home_username", "children"),
    Output("home_email", "children"),
    Input("session", "data"),
)
def set_info(session_data: Dict) -> Tuple[str, str, str]:
    username_desc = ""
    email_desc = ""
    if "current_user" not in session_data.keys():
        return (username_desc, email_desc)
    cur_user_info = session_data["current_user"]
    username_desc = f"Username: {cur_user_info['name']}"
    email_desc = f"Email: {cur_user_info['email']}"
    return (username_desc, email_desc)


def get_user_description():
    user_description = dbc.Col(
        [
            dbc.Col(dbc.Label(id="home_username")),
            dbc.Col(html.Hr()),
            dbc.Col(dbc.Label(id="home_email")),
        ]
    )
    return user_description


def layout():
    user_description = get_user_description()
    layout = html.Div(
        [
            html.H5("Profile", style={"margin-top": "5%", "margin-left": "5%"}),
            html.Div(
                children=[user_description],
                style={"margin-right": "5%", "margin-left": "5%", "margin-top": "5%"},
            ),
        ]
    )
    return layout
