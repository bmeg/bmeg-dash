import flask
import dash
import yaml
import dash_bootstrap_components as dbc

with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
path_name = config['DEV']['basepath']

server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/' + path_name + '/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1"
        }
    ],
)
app.config.suppress_callback_exceptions = True
