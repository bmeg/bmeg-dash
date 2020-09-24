from .. import appLayout as ly
from ..app import app
from ..db import G, gene_search
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import dash_bio
import dash_cytoscape as cyto
import gripql
import json
import pandas as pd
from plotly.subplots import make_subplots
import logging
logger = logging.getLogger(__name__)

#######
# Prep
#######

main_colors= ly.main_colors
styles=ly.styles


pathwayList = []
for row in G.query().V().hasLabel("Pathway").render([ "$._gid", "$.name"]):
    pathwayList.append( [row[0], row[1].lower()] )

element = cyto.Cytoscape(
    id='bmeg-cytoscape',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '400px', 'arrow-scale': 2, 'target-arrow-shape': 'vee'},
    elements=[
        {'data': {'id': 'one', 'label': 'Node 1'} },
        {'data': {'id': 'two', 'label': 'Node 2'} },
        {'data': {'source': 'one', 'target': 'two'}}
    ]
)

NAME="Pathway View"
tab_layout = html.Div(children=[
    html.Label("Pathway:"), dcc.Dropdown(id='pathway-dropdown'),
    element
])


@app.callback(
    dash.dependencies.Output('pathway-dropdown', 'options'),
    [dash.dependencies.Input('pathway-dropdown', 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    hits = []
    for g, n in pathwayList:
        if search_value in n:
            hits.append( {"label" : n, "value" : g} )
    return hits
