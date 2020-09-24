from .. import appLayout as ly
from ..app import app
from ..components import home_component as dty
from ..db import G, get_vertex_label_count
from bmeg_app.views import home_view, tumor_match_normal_view, literature_support_view, compare_dresp_view
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
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
NAME="Home"
LAYOUT = html.Div(children=[
    html.H4(children='What is stored inside the database?',style=styles['sh']),
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4("Identify Drug Treatment Candidates from Cancer Cell Line Drug Screens"),
                html.P("Interrogate cell line drug screening trials from large established sources (CCLE, CTRP, GDSC). Dig into drug sensitivity trends within a particular disease and explore associated metadata."),
                html.P("For example, select a FDA drug that is widely known to prevent/treat a particular disease phenotype (ex. Paclitaxel, breast cancer treatment) and identify other drugs that show a similar impact on cell lines."),
                dbc.Button(
                    dbc.NavLink('Cancer Drug Screening',href='/drug_response',id='page2-link'),color='light'
                ),
            ],
        )
    ),

    dbc.Card(
        dbc.CardBody(
            [
                html.H4("Tumor vs. Normal", className="card-title"),
                html.P("Some descriptive text here on the purpose and use of this widget. Info on the type of data used in this widget"),
                dbc.Button(
                    dbc.NavLink('TCGA Clustering',href='/tumors',id='page3-link'),color="light"
                ),
            ]
        )
    ),

    dbc.Card(
        dbc.CardBody(
            [
                html.H4("Curated Literature Evidence", className="card-title"),
                html.P("Some descriptive text here on the purpose and use of this widget. Info on the type of data used in this widget"),
                dbc.Button(
                    dbc.NavLink('Literature Gene-Drug Associations',href='/g2p',id='page4-link'),color="light"
                ),


            ]
        )
    ),
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
        res[l] = get_vertex_label_count(l)
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
        res[l] = get_vertex_label_count(l)
    keys=[]
    values=[]
    for k,v in res.items():
        keys.append(k)
        values.append(v)
    fig = dty.bar('','Node', keys, values, main_colors['pale_yellow'], 250, '', '')
    return dcc.Graph(id='node_cts_bar_output', figure=fig),
