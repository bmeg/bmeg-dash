import flask
import dash
import dash_bootstrap_components as dbc

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname = '/',external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions=True
