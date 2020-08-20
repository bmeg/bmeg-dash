import flask
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)

# No docker, local 
app = dash.Dash(__name__, server=server, url_base_pathname = '/',external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__, server=server, url_base_pathname = '/', external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions=True
