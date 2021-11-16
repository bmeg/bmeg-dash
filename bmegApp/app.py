
from . import config
import os
import sys
import flask
import dash
import yaml
import i18n
import base64

import dash_bootstrap_components as dbc

BASEDIR = os.path.dirname( os.path.abspath(__file__) )

path_name = config.CONFIG[config.STAGE]['basepath']


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
