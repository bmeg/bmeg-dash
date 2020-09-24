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

def getGeneMutations(gene):
    app.logger.info("Updating mutation Track")
    res = G.query().V(gene).out("alleles").as_("a").outE("somatic_callsets").as_("c").render(["$a.ensembl_transcript", "$a.cds_position", "$c._to"])
    o = []
    t = []
    for transcript, cds, dst in res:
        v = cds.split("/")[0]
        try:
            d = int(v)
            o.append(d)
        except ValueError:
            pass
        t.append(transcript)
    logger.info("Transcript %s" % (set(t)))
    df = pd.Series(o)
    counts = df.value_counts()
    mData = {
        "x" : list("%d.0" % (i) for i in counts.index),
        "y" : list("%d" % (i) for i in counts.values)
    }
    return mData
#print(json.dumps(mData))

component = dash_bio.NeedlePlot(
  id='my-dashbio-needleplot',
  mutationData={},
  needleStyle={
        'stemColor': '#FF8888',
        'stemThickness': 2,
        #'stemConstHeight': True,
        'headSize': 10,
        'headColor': ['#FFDD00', '#000000']
  }
)


#######
# Page
#######
NAME="Gene-level Mutation View"
LAYOUT = html.Div(children=[
    html.Label("Gene:"), dcc.Dropdown(id='single-dropdown', value="TP53/ENSG00000141510", search_value="TP53/ENSG00000141510"),
    component,
    html.Div(id='needle-selection')
])

@app.callback(
    dash.dependencies.Output('single-dropdown', 'options'),
    [dash.dependencies.Input('single-dropdown', 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    return genes


@app.callback(
    dash.dependencies.Output('my-dashbio-needleplot', 'mutationData'),
    [dash.dependencies.Input('single-dropdown', 'value')])
def process_single(value):
    if not value:
        raise PreventUpdate
    gene = value.split("/")[1]
    app.logger.info("Getting: %s" % (gene))
    return getGeneMutations(gene)


@app.callback(
    Output('needle-selection', 'children'),
    [Input('my-dashbio-needleplot', 'selectedData')])
def display_selected_data(selectedData):
    #This doesn't seem to respond so will probably delete
    app.logger.info("Got selectedData")
    return json.dumps(selectedData, indent=2)
