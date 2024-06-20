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
    Output("session", "data"),
    Output("login_successful", "is_open"),
    Output("login_missing-data", "is_open"),
    Output("login_error", "is_open"),
    Input("login_button", "n_clicks"),
    State("session", "data"),
    State("login_form_email", "value"),
    State("login_form_password", "value"),
)
def login_user(
    n_clicks: int, session_data: Dict, login_email: str, login_password: str
) -> Tuple[Dict, bool, bool, bool]:
    if n_clicks is None:
        raise PreventUpdate
    login_successful = False
    login_missing_data = False
    login_error = False
    if n_clicks == 0:
        return session_data, login_successful, login_missing_data, login_error
    if None in [login_email, login_password]:
        login_missing_data = True
        return session_data, login_successful, login_missing_data, login_error
    response: Response = login_via_api(email=login_email, password=login_password)
    if response.status_code == HTTPStatus.OK:
        token = response.json()["access_token"]
        session_data["token"] = token
        cur_user_response = get_current_user_data_via_api(access_token=token)
        session_data["current_user"] = cur_user_response.json()
        login_successful = True
        return session_data, login_successful, login_missing_data, login_error

    login_error = True
    return session_data, login_successful, login_missing_data, login_error


def get_login_form():
    form = dbc.Form(
        dbc.Row(
            [
                dbc.Label("Email", width="auto"),
                dbc.Col(
                    dbc.Input(
                        type="email", id="login_form_email", placeholder="Enter email"
                    ),
                    className="me-3",
                ),
                dbc.Label("Password", width="auto"),
                dbc.Col(
                    dbc.Input(
                        type="password",
                        id="login_form_password",
                        placeholder="Enter password",
                    ),
                    className="me-3",
                ),
                dbc.Col(
                    dbc.Button("Login", id="login_button", color="primary", n_clicks=0),
                    width="auto",
                ),
            ],
            className="g-2",
        )
    )
    return form


def layout():
    form = get_login_form()
    layout = html.Div(
        [
            dbc.Alert(
                "Successfully logged in",
                color="success",
                id="login_successful",
                is_open=False,
                duration=1000,
            ),
            dbc.Alert(
                "Please fill the sign up form",
                color="warning",
                id="login_missing-data",
                is_open=False,
                duration=1000,
            ),
            dbc.Alert(
                "Could not log in with these credentials",
                color="danger",
                id="login_error",
                is_open=False,
                duration=1000,
            ),
            html.H5("Login", style={"margin-top": "5%", "margin-left": "5%"}),
            html.Div(
                children=[form], style={"margin-right": "5%", "margin-left": "5%"}
            ),
        ]
    )
    return layout
