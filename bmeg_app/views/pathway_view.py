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


def getPathwayGraph(pathway):
    q = G.query().V(pathway).out("interactions").as_("i")
    q = q.in_("interaction_input").as_("in").select("i")
    q = q.out("interaction_output").as_("out").select("o")
    q = q.render(["$in._gid", "$i._gid", "$out._gid"])

    nodes = set()
    data = []
    for src, inter, dst in q:
        if src not in nodes:
            data.append( { "data" : {"id" : src, "label" : src} } )
        if dst not in nodes:
            data.append( { "data" : {"id" : dst, "label" : dst} } )
        data.append( { "data" : { "source" : src, "target" : dst} } )
    return data

element = cyto.Cytoscape(
    id='bmeg-cytoscape',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '400px', 'arrow-scale': 2, 'target-arrow-shape': 'vee'},
    elements=[]
)

NAME="Pathway View"
LAYOUT = html.Div(children=[
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

@app.callback(
    dash.dependencies.Output('bmeg-cytoscape', 'elements'),
    [dash.dependencies.Input('pathway-dropdown', 'value')]
)
def update_pathway(value):
    app.logger.info("Getting pathway: %s" % (value))
    out = getPathwayGraph(value)
    app.logger.info("%s has %d elements" % (value, len(out)))
    return out