import flask
import dash
import dash_bootstrap_components as dbc

server = flask.Flask(__name__)
# app = dash.Dash(__name__, server=server, url_base_pathname = '/',external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(
    __name__, server=server, url_base_pathname = '/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
app.config.suppress_callback_exceptions=True
