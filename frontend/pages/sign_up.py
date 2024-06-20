import dash
from http import HTTPStatus
from requests import Response
from dash import Dash, html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from frontend.api_utils import register_user_via_api
from typing import Dict, List, Tuple

dash.register_page(__name__)


@callback(
    Output("register-successful", "is_open"),
    Output("register_missing-data", "is_open"),
    Output("register_error", "is_open"),
    Input("signup-button", "n_clicks"),
    # form data
    State("register_form_username", "value"),
    State("register_form_email", "value"),
    State("register_form_pwd", "value"),
)
def register_user(
    n_clicks: int, user_name: str, user_email: str, user_password: str
) -> Tuple[bool, bool, bool]:
    if n_clicks is None:
        raise PreventUpdate
    register_successful = False
    register_missing_data = False
    register_error = False
    if n_clicks == 0:
        return register_successful, register_missing_data, register_error
    if None in [user_email, user_password]:
        register_missing_data = True
        return register_successful, register_missing_data, register_error
    print(user_name, user_email, user_password)
    print(user_name, user_email, user_password)
    response: Response = register_user_via_api(
        username=user_name, email=user_email, password=user_password
    )
    if response.status_code == HTTPStatus.OK:
        register_successful = True
        return register_successful, register_missing_data, register_error
    register_error = True
    return register_successful, register_missing_data, register_error


def get_signup_form():
    email_input = html.Div(
        [
            dbc.Input(
                type="email", id="register_form_email", placeholder="Enter email"
            ),
        ],
        className="mb-3",
    )

    username_input = html.Div(
        [
            dbc.Input(
                type="text", id="register_form_username", placeholder="Enter username"
            ),
        ],
        className="mb-3",
    )

    password_input = html.Div(
        [
            dbc.Input(
                type="password",
                id="register_form_pwd",
                placeholder="Enter password",
            ),
        ],
        className="mb-3",
    )
    signup_button = dbc.Button(
        "Sign Up", id="signup-button", color="primary", n_clicks=0
    )
    sign_up_form = dbc.Form(
        [email_input, username_input, password_input, signup_button],
        style={"margin-right": "5%", "margin-left": "5%"},
    )
    return sign_up_form


def layout():
    sign_up_form = get_signup_form()
    layout = html.Div(
        [
            dbc.Alert(
                "Successfully registered",
                color="success",
                id="register-successful",
                is_open=False,
                duration=1000,
            ),
            dbc.Alert(
                "Please fill the sign up form",
                color="warning",
                id="register_missing-data",
                is_open=False,
                duration=1000,
            ),
            dbc.Alert(
                "Could not register",
                color="danger",
                id="register_error",
                is_open=False,
                duration=1000,
            ),
            html.H5("Sign Up", style={"margin-top": "5%", "margin-left": "5%"}),
            html.Div(children=[sign_up_form]),
            html.Span(id="hidden-signup-span", style={"display": "none"}),
        ]
    )
    return layout
