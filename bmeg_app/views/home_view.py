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
import i18n
i18n.load_path.append('bmeg_app/locales/')

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles

#######
# Page
#######
NAME=i18n.t('app.config.tabname_widget_home')
LAYOUT = html.Div(children=[
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4(i18n.t('app.widget_home.cluster.header'), className="card-title"),
                html.P(i18n.t('app.widget_home.cluster.body')),
                dbc.Button(
                    dbc.NavLink(i18n.t('app.widget_home.cluster.button'),href=i18n.t('app.widget_home.cluster.href')),color="light"
                ),
            ]
        )
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4(i18n.t('app.widget_home.lit.header'), className="card-title"),
                html.P(i18n.t('app.widget_home.lit.body')),
                dbc.Button(
                    dbc.NavLink(i18n.t('app.widget_home.lit.button'),href=i18n.t('app.widget_home.lit.href')),color="light"
                ),


            ]
        )
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4(i18n.t('app.widget_home.dresp.header')),
                html.P(i18n.t('app.widget_home.dresp.body')),
                html.P(i18n.t('app.widget_home.dresp.body2')),
                dbc.Button(
                    dbc.NavLink(i18n.t('app.widget_home.dresp.button'),href=i18n.t('app.widget_home.dresp.href')),color='light'
                ),
            ],
        )
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4(i18n.t('app.widget_home.gmut.header')),
                html.P(i18n.t('app.widget_home.gmut.body')),
                dbc.Button(
                    dbc.NavLink(i18n.t('app.widget_home.gmut.button'),href=i18n.t('app.widget_home.gmut.href')),color='light'
                ),
            ],
        )
    ),
    dbc.Card(
        dbc.CardBody(
            [
                html.H4(i18n.t('app.widget_home.pathway.header')),
                html.P(i18n.t('app.widget_home.pathway.body')),
                dbc.Button(
                    dbc.NavLink(i18n.t('app.widget_home.pathway.button'),href=i18n.t('app.widget_home.pathway.href')),color='light'
                ),
            ],
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
