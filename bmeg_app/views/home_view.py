from ..app import app
from ..components import home_component as dty
from ..db import G, get_vertex_label_count
from ..style import format_style, color_palette
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import i18n
import yaml

with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
path_name = config['DEV']['basepath']

i18n.load_path.append('bmeg_app/locales/')

#######
# Page
#######
NAME = i18n.t('app.config.tabname_widget_home')


def CREATE(index):
    return html.Div(
        children=[
            # html.H1(
            #    i18n.t('app.config.banner'),
            #    style=format_style('banner')
            # ),
            dcc.Loading(
                id={"type":"summary-counts", "index":index},
                type="default",
                children=html.Div(id="cards_output")
            ),
            html.Br(),
            dcc.Loading(
                id={"type":"summary-counts-barchart", "index":index},
                type="default",
                children=html.Div(id="node_cts_bar_output")
            ),
        ],
        style={'fontFamily': format_style('font'), 'border': '2px solid'}
    )


@app.callback(
    Output({"type":"summary-counts", "index":MATCH}, "children"),
    [Input('url', 'pathname')]
)
def render_callback(href):
    '''Number counts'''
    nodes_interest = [
        'Allele', 'Gene',
        'Transcript', 'Exon',
        'Protein', 'DrugResponse',
        'Pathway', 'Compound',
        'Interaction', 'Project',
        'Publication', 'Aliquot'
    ]
    res = {}
    for node in nodes_interest:
        res[node] = get_vertex_label_count(node)
    fig = dty.counts(
        100,
        res,
    )
    return dcc.Graph(id='cards_output', figure=fig),


@app.callback(
    Output({"type":"summary-counts-barchart", "index":MATCH}, "children"),
    [Input('url', 'pathname')]
)
def render_node_cts_bar(href):
    '''Bar chart counts'''
    all_v = G.listLabels()['vertexLabels']
    to_rm = [
        'Aliquot', 'Allele',
        'Gene', 'Protein',
        'Transcript', 'Exon',
        'Pathway', 'Compound',
        'DrugResponse', 'Interaction',
        'Project', 'Publication'
    ]
    verts = [x for x in all_v if x not in to_rm]
    res = {}
    for ver in verts:
        res[ver] = get_vertex_label_count(ver)
    keys = []
    values = []
    for k, v in res.items():
        keys.append(k)
        values.append(v)
    fig = dty.bar(
        '',
        'Node',
        keys,
        values,
        color_palette('lightgreen_borderfill'),
        250,
        '',
        ''
    )
    return dcc.Graph(id='node_cts_bar_output', figure=fig),
