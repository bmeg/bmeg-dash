from .. import appLayout as ly
from ..app import app
from ..components import literature_support_component as lsu
from ..db import G, gene_search
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import gripql
import json
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
print('loading app layout')
NAME= i18n.t('app.config.tabname_lit')
LAYOUT = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.Label(i18n.t('app.widget_lit.menu1')),
                        dcc.Dropdown(id='gene_dd',
                            value="MTOR/ENSG00000198793", search_value="MTOR/ENSG00000198793"
                        ),
                    ],style={'width': '100%','display': 'inline-block','font-size' : styles['t']['size_font']}
                ),
            ),
        ]
    ),
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(html.Div(id='occr', children=html.Div()),width=3,style={"c":"100%"}),
            dbc.Col(html.Div(id='resp_histo', children=html.Div()),width=4,style={"height":"100%"}),
            dbc.Col(html.Div(id='pie_taxon', children=html.Div()),width=5,style={"height":"100%"}),

        ],
    ),
    html.Hr(),
    html.Div(id='evd', children=html.Div()),
],style={'fontFamily': styles['t']['type_font']})


@app.callback(
    dash.dependencies.Output('gene_dd', 'options'),
    [dash.dependencies.Input('gene_dd', 'search_value')]
)
def update_options(search_value):
    """Lookup the search value in elastic."""
    if not search_value:
        raise PreventUpdate
    genes = gene_search(search_value)
    return genes

@app.callback(
    [Output("evd", "children"), Output("resp_histo", "children"),Output("pie_taxon", "children"), Output("occr", "children")],
    [Input('gene_dd', 'value')]
)
def build_evidence_table(search_value):
    gene = search_value.split("/")[1]
    '''Occurance table'''
    mapping = {
        "id" : "$._gid",
        "evidence_label" : "evidence_label",
        "oncogenic": "oncogenic",
        "response_type" : "response_type",
        "source" : "source"
    }
    g2p = []
    response = []
    for row in G.query().V(gene).out("g2p_associations").render(mapping):
        g2p.append(row.to_dict())
        response.append(row['response_type'])

    '''Occurance table'''
    evidence_table = dash_table.DataTable(
        id='export_g2p_table',
        data = g2p,
        columns=[{"name": i, "id": i} for i in ["evidence_label", "oncogenic", "response_type", "source"]],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        #tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        page_size=10,
    )

    pub_table = dash_table.DataTable(
        id='export_pub_table',
        data = g2p,
        columns=[{"name": i, "id": i} for i in ["evidence_label", "oncogenic", "response_type", "source"]],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        #tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        page_size=10,
    )

    #fig= px.histogram(response, orientation="h")
    #histogram = html.Div(dcc.Graph(figure=fig)),
    histogram = html.Div(dcc.Graph())

    '''pie chart compound taxonomy'''
    associated_compounds = G.query().V(gene).out("g2p_associations").as_("a").out("compounds").as_("c").render(["$a._gid", "$c._gid"]).execute()

    c = [] #G.query().V(list(pd.DataFrame(associated_compounds)[1].unique())).render(["_gid", "taxonomy.superclass"]).execute()
    compound_info = pd.DataFrame(c, columns=["id", "superclass"]).set_index("id")
    pie_chart = dcc.Graph(figure=px.pie(compound_info, names="superclass"))

    return html.Div(pub_table), histogram, pie_chart, html.Div(evidence_table)
