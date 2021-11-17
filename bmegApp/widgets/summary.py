
from dash.dependencies import Input, Output, State, ALL, MATCH
from ..app import app
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
from ..style import format_style, color_palette
from ..db import G, get_vertex_label_count
from ..components import home_component as dty

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
        'Project', 'Publication', 'TranscriptExpression'
    ]
    verts = [x for x in all_v if x not in to_rm]
    res = {}
    for ver in verts:
        print("Doing search", ver)
        res[ver] = get_vertex_label_count(ver)
    print("Search done")
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
    print("Chart done")
    return dcc.Graph(id='node_cts_bar_output', figure=fig),