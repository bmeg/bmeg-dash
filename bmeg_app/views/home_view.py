from ..app import app
from ..components import home_component as dty
from ..db import G, get_vertex_label_count
from ..style import format_style, color_palette
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
# Page
#######
NAME=i18n.t('app.config.tabname_widget_home')

cluster_card=dty.build_card(
    i18n.t('app.widget_home.cluster.header'),
    [i18n.t('app.widget_home.cluster.body')],
    i18n.t('app.widget_home.cluster.button'),
    i18n.t('app.widget_home.cluster.href')
)
lit_card=dty.build_card(
    i18n.t('app.widget_home.lit.header'),
    [i18n.t('app.widget_home.lit.body')],
    i18n.t('app.widget_home.lit.button'),
    i18n.t('app.widget_home.lit.href')
)
# dresp_card=dty.build_card(i18n.t('app.widget_home.dresp.header'),[i18n.t('app.widget_home.dresp.body'),i18n.t('app.widget_home.dresp.body2')],i18n.t('app.widget_home.dresp.button'),i18n.t('app.widget_home.dresp.href') )
dresp_card=dty.build_card(
    i18n.t('app.widget_home.dresp.header'),
    [i18n.t('app.widget_home.dresp.body')],
    i18n.t('app.widget_home.dresp.button'),
    i18n.t('app.widget_home.dresp.href')
)
# gene_mut_card=dty.build_card(
#     i18n.t('app.widget_home.gmut.header'),
#     [i18n.t('app.widget_home.gmut.body')],
#     i18n.t('app.widget_home.gmut.button'),
#     i18n.t('app.widget_home.gmut.href')
# )
# pathway_card=dty.build_card(
#     i18n.t('app.widget_home.pathway.header'),
#     [i18n.t('app.widget_home.pathway.body')],
#     i18n.t('app.widget_home.pathway.button'),
#     i18n.t('app.widget_home.pathway.href')
# )

LAYOUT = html.Div(children=[
    html.H1('Bio Medical Evidence Graph (BMEG)',style=format_style('banner')),
    dcc.Loading(id="cards",
            type="default",children=html.Div(id="cards_output")),
    html.Br(),
    dcc.Loading(id="node_cts_bar",
            type="default",children=html.Div(id="node_cts_bar_output")),
    html.H3('Analysis Widgets',style=format_style('subbanner')),
    dbc.Row(
        [
            dbc.Col(lit_card),
            dbc.Col(dresp_card),
        ]
    ),
    # html.Br(),
    # dbc.Row(
    #     [
    #         dbc.Col(gene_mut_card),
    #         dbc.Col(pathway_card),
    #     ]
    # ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(cluster_card),
        ]
    ),
],style={'fontFamily':format_style('font')})


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
    fig= dty.counts(100, res, color_palette('lightgrey'),format_style('font'))
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
    fig = dty.bar('','Node', keys, values, color_palette('lightgreen_borderfill'), 250, '', '')
    return dcc.Graph(id='node_cts_bar_output', figure=fig),
