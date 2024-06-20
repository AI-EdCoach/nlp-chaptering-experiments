import dash
from dash import Dash, html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pprint import pprint

dash.register_page(__name__, top_nav=True, path="/")


def layout():
    layout = html.Div(
        style={
            "background-image": "url(assets/welcome_page_bg.jpg)",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "background-position": "center",
            "height": "100vh",
        },
    )
    return layout
