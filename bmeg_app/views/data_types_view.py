from .. import appLayout as ly
from ..app import app
from ..components import data_types_component as dty
from ..db import G
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import gripql
import pandas as pd
import plotly.express as px

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles

#######
# Page
#######
NAME="Main"
tab_layout = html.Div(children=[
    html.H4(children='What is stored inside the database?',style=styles['sh']),
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
],style={'fontFamily': styles['t']['type_font'],})


@app.callback(
    Output("cards", "children"),
    [Input('url', 'pathname')]
)
def render_callback(href):
    '''Number counts'''
    if href is None:
        raise PreventUpdate
    nodes_interest = ['Allele','Gene','Transcript','Exon','Protein','DrugResponse', 'Pathway','Compound', 'Interaction','Project','Publication', 'Aliquot']
    res = {}
    for l in nodes_interest:
        res[l] = G.query().V().hasLabel(l).count().execute()[0]['count']
    fig= dty.counts(100, res,main_colors['lightgrey'],styles['t']['type_font'])
    return dcc.Graph(id='cards_output', figure=fig),

@app.callback(
    Output("node_cts_bar", "children"),
    [Input('url', 'pathname')]
)
def render_callback(href):
    '''Bar chart counts'''
    if href is None:
        raise PreventUpdate
    all_v =  G.listLabels()['vertex_labels']
    to_rm = ['Aliquot','Allele', 'Gene', 'Protein', 'Transcript', 'Exon','Pathway', 'Compound', 'DrugResponse', 'Interaction','Project', 'Publication']
    verts = [x for x in all_v if x not in to_rm]
    res = {}
    for l in verts:
        res[l] = G.query().V().hasLabel(l).count().execute()[0]['count']
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig = dty.bar('','Node', keys, values, main_colors['pale_yellow'], 250, '', '')
    return dcc.Graph(id='node_cts_bar_output', figure=fig),
