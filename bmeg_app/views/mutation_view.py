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

#######
# Prep
#######

main_colors= ly.main_colors
styles=ly.styles

def getGeneMutations(gene):
    cds = G.query().V(gene).out("alleles").render("cds_position").execute()
    o = []
    for i in cds:
        v = i.split("/")[0]
        try:
            d = int(v)
            o.append(d)
        except ValueError:
            pass
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
print('loading app layout')
NAME="OncoPrint"
tab_layout = html.Div(children=[
    html.Label("Gene:"), dcc.Dropdown(id='single-dropdown'),
    component
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
    return getGeneMutations(gene)
