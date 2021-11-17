import os
from ..app import app
from ..widgets import summary
from ..components import home_component as dty
from ..db import G, get_vertex_label_count
from ..style import format_style, color_palette
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL, MATCH
import i18n
import yaml


#######
# Page
#######
NAME = i18n.t('app.config.tabname_widget_home')

def CREATE(index):
    return summary.CREATE(index)
