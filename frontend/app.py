import os
from dotenv import load_dotenv
import dash
import json
from dash import Dash, dcc, html, Input, Output, callback, State
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import plotly.express as px
from pprint import pprint
from typing import List, Dict


load_dotenv()
load_figure_template("LUX")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.LUX],
)


@callback(Output("app-navbar", "children"), Input("login_session", "data"))
def set_navbar(session_data: Dict) -> Dict:
    print(f"set navbar based on {session_data}")
    items = non_authorized_user_navbar_items()
    if session_data["token"] is not None:
        items = authorized_user_navbar_items()
    return items


def get_auth_navbar_items() -> List[dbc.NavItem]:
    login_page = dash.page_registry["pages.login"]
    sign_up_page = dash.page_registry["pages.sign_up"]
    login_item = dbc.NavItem(dbc.NavLink("Login", href=login_page["relative_path"]))
    sign_up_item = dbc.NavItem(
        dbc.NavLink("Sign up", href=sign_up_page["relative_path"])
    )
    return [login_item, sign_up_item]


def get_authorized_navbar_dropdown_menu() -> dbc.DropdownMenu:
    models_page = dash.page_registry["pages.video_analytics"]
    profile_page = dash.page_registry["pages.user_profile"]
    dropdown = dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem("Profile", href=profile_page["relative_path"]),
            dbc.DropdownMenuItem("EdCoach", href=models_page["relative_path"]),
        ],
        nav=True,
        in_navbar=True,
        label="MORE",
    )
    return dropdown


def non_authorized_user_navbar_items() -> List:
    auth_navbar_items = get_auth_navbar_items()
    return auth_navbar_items


def authorized_user_navbar_items() -> List:
    all_navbar_items = get_auth_navbar_items()
    drodown_items = get_authorized_navbar_dropdown_menu()
    all_navbar_items.append(drodown_items)
    return all_navbar_items


def create_navbar():
    navbar_items = non_authorized_user_navbar_items()
    navbar = dbc.NavbarSimple(
        id="app-navbar",
        children=navbar_items,
        brand="AIEdCoach",
        brand_href="/",
        color="primary",
        dark=True,
        brand_style={
            "margin-left": "2%",
            "font-size": "30px",
            "font-weight": "bolder",
        },
        fluid=True,
    )
    return navbar


def create_layout():
    navbar = create_navbar()
    app.layout = html.Div(
        [
            navbar,
            dash.page_container,
            dcc.Store(id="login_session", storage_type="memory", data={"token": None}),
            dcc.Store(
                id="uploaded_video_session", storage_type="memory", data={"token": None}
            ),
            dcc.Store(
                id="timecodes_session", storage_type="memory", data={"token": None}
            ),
        ]
    )


if __name__ == "__main__":
    create_layout()
    app.run(host="0.0.0.0", debug=False, port=os.environ["FRONTEND_PORT"])
