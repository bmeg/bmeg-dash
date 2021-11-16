from ..app import app
from ..components import info_button
from ..db import G, gene_search
from ..style import format_style
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, MATCH
import dash_html_components as html
import dash_table
import gripql
import json
import pandas as pd
import plotly.express as px
import i18n
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASEDIR, '../locales/data.json'), 'r') as fh:
    bins_dict = json.load(fh)["response_bins"]

#######
# Page
#######
print('loading app layout')
NAME = i18n.t('app.config.tabname_lit')

def CREATE(index):
    return html.Div(
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(i18n.t('app.widget_lit.menu1')),
                                dcc.Dropdown(
                                    id={"type": 'lit-gene-dd', "index":index},
                                    value="MTOR/ENSG00000198793",
                                    search_value="MTOR/ENSG00000198793"
                                ),
                            ],
                            style={
                                'width': '100%',
                                'display': 'inline-block',
                                'font-size': format_style('font_size')
                            }
                        ),
                    ),
                    dbc.Col(
                        html.Div(
                            info_button(
                                'help_indicator',
                                i18n.t('app.widget_lit.button_body')
                            )
                        ),
                        width='1'
                    ),
                ]
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id={"type": 'lit-gene-occr', "index":index},
                            children=html.Div()
                        ),
                        width=2,
                        style={"height": "100%"}
                    ),
                    dbc.Col(
                        dcc.Loading(
                            id={"type": 'lit-gene-resp-histo', "index":index},
                            children=html.Div()
                        ),
                        width=4,
                        style={"height": "100%"}
                    ),
                    dbc.Col(
                        dcc.Loading(
                            id={"type": 'lit-gene-pie-taxon', "index":index},
                            children=html.Div()
                        ),
                        width=6,
                        style={"height": "100%"}
                    ),

                ],
            ),
            html.Hr(),
            dcc.Loading(id={"type":'lit-gene-evd', "index":index}, children=html.Div()),
        ],
        style={'fontFamily': format_style('font')}
    )


@app.callback(
    Output({"type":"lit-gene-dd", "index":MATCH}, 'options'),
    [Input({"type":"lit-gene-dd", "index":MATCH}, 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    return genes


@app.callback(
    [
        Output({"type":"lit-gene-evd", "index":MATCH}, "children"),
        Output({"type":"lit-gene-resp-histo", "index":MATCH}, "children"),
        Output({"type":"lit-gene-pie-taxon", "index":MATCH}, "children"),
        Output({"type":"lit-gene-occr", "index":MATCH}, "children")
    ],
    [Input({"type":"lit-gene-dd", "index":MATCH}, 'value')]
)
def build_evidence_table(search_value):
    gene = search_value.split("/")[1]
    '''Occurance table'''
    # Associations
    mapping = {
        "id": "$._gid",
        "evidence_label": "evidence_label",
        "oncogenic": "oncogenic",
        "response_type": "response_type",
        "source": "source"
    }
    g2p = []
    response = []
    for row in G.query().V(gene).out("g2p_associations").render(mapping):
        g2p.append(row)
        if row['response_type'] in bins_dict:
            response.append(bins_dict.get(row['response_type']))
        else:
            try:
                response.append(row['response_type'].capitalize())
            except AttributeError:
                response.append(row['response_type'])
    # If no responses found exit
    if len(response) == 0:
        message = [
            html.Label('No Responses Found'),
            html.Label('No Responses Found'),
            html.Label('No Responses Found'),
            html.Label('No Responses Found')
        ]
        return message
    g2p_chem = {}
    q = G.query().V(gene).out("g2p_associations").as_("a") \
        .out("compounds").as_("c") \
        .render(["$a._gid", "$c._gid", "$c.synonym"])
    for row in q.execute():
        if row[0] in g2p_chem:
            g2p_chem[row[0]].append(row[2])
        else:
            g2p_chem[row[0]] = [row[2]]
    g2p_cite = {}
    q = G.query().V(gene).out("g2p_associations").as_("a") \
        .out("publications").as_("c") \
        .render(["$a._gid", "$c.url", "$c.title"])
    for row in q:
        if row[0] in g2p_cite:
            g2p_cite[row[0]].append((row[1], row[2]))
        else:
            g2p_cite[row[0]] = [(row[1], row[2])]

    rows = []
    for g in g2p:
        if g["id"] in g2p_cite:
            for c in g2p_cite[g["id"]]:
                row = dict(**g)
                if row["id"] in g2p_chem:
                    row['compound'] = ", ".join(
                        list(
                            i.capitalize() for i in g2p_chem[row["id"]] if i
                        )
                    )
                row['title'] = "[%s](%s)" % (c[1] if c[1] else c[0], c[0])
                rows.append(row)

    '''Occurance table'''
    table_columns = [
        {"name": "Title", "id": "title", 'presentation': 'markdown'},
        {"name": "Compounds", "id": "compound"},
        {"name": "Source", "id": "source"},
        {"name": "Response", "id": "response_type"},
        {"name": "Evidence Level", "id": "evidence_label"}
    ]

    evidence_table = dash_table.DataTable(
        id='export_g2p_table',
        data=rows,
        columns=table_columns,
        style_header={
            'text-align': 'center',
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontSize': format_style('font_size'),
            'fontWeight': 'bold',
            'fontFamily': format_style('font')
        },
        style_cell={
            'maxWidth': '100px',
            'padding-left': '20px',
            'padding-right': '20px'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'text-align': 'center',
            'fontFamily': format_style('font'),
            'fontSize': format_style('font_size')
        },
        style_data_conditional=[
            {
                'if': {
                    'row_index': 'odd'
                },
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_table={'overflow': 'hidden'},
        style_as_list_view=True,
        tooltip_duration=None,
        page_size=10,
    )

    citations = G.query().V(gene).out("g2p_associations").as_("a")\
        .out("publications").as_("p") \
        .select("a") \
        .out("compounds").as_("c") \
        .aggregate(gripql.term("chem_citation", "$c.synonym")).execute()
    citation_counts = []
    print("Agg results: %s" % (citations))
    for i in citations[0]["chem_citation"]["buckets"]:
        citation_counts.append(
            {"compound": i['key'].capitalize(), "citations": i['value']}
        )

    pub_table = dash_table.DataTable(
        id='export_pub_table',
        data=citation_counts[:10],
        columns=[
            {"name": "Top 10", "id": "compound"},
            {"name": "Citations", "id": "citations"}
        ],
        style_header={
            'text-align': 'center',
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontSize': format_style('font_size'),
            'fontWeight': 'bold',
            'fontFamily': format_style('font')
        },
        style_cell={
            'maxWidth': '100px',
            'padding-left': '20px',
            'padding-right': '20px'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'text-align': 'center',
            'fontFamily': format_style('font'),
            'fontSize': format_style('font_size_sm')
        },
        style_data_conditional=[
            {
                'if': {
                    'row_index': 'odd'
                },
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_table={'overflow': 'hidden'},
        style_as_list_view=True,
        tooltip_duration=None,
        page_size=10,
    )

    height = 310

    fig = px.histogram(
        response,
        orientation="h",
        height=height,
        title="Cell Line Response",
        labels={'count': 'Count', 'value': ''}
    )
    fig.update_layout(
        margin={'t': 25, 'b': 0, 'r': 0},
        yaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    histogram = dcc.Graph(figure=fig)

    '''pie chart compound taxonomy'''
    associated_compounds = G.query().V(gene).out("g2p_associations").as_("a") \
        .out("compounds").as_("c") \
        .render(["$a._gid", "$c._gid"]).execute()
    c = G.query().V(
        list(
            pd.DataFrame(associated_compounds)[1].unique()
        )
    ).render(["_gid", "taxonomy.superclass"]).execute()
    compound_info = pd.DataFrame(
        c,
        columns=["id", "superclass"]
    ).set_index("id")

    # Remove NA superclasses
    subset = compound_info.dropna()
    na_dropped = len(compound_info.index)-len(subset.index)

    fig = px.pie(
        subset,
        names="superclass",
        height=height,
        title="Compound Superclass \
            ({} without superclass info)".format(na_dropped)
    )
    fig.update_layout(showlegend=False, margin={'t': 25, 'b': 0})
    fig.update_traces(textinfo='label')
    pie_chart = dcc.Graph(figure=fig)
    return evidence_table, histogram, pie_chart, pub_table
