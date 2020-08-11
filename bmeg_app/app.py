import flask
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)

# No docker, local 
app = dash.Dash(__name__, server=server, url_base_pathname = '/', external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions=True
