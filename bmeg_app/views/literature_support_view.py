from .. import appLayout as ly
from ..app import app
from ..components import literature_support_component as lsu
from ..db import G
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import gripql
import json
import pandas as pd
from plotly.subplots import make_subplots

#######
# Prep
#######
main_colors= ly.main_colors
styles=ly.styles
# base_df = lsu.get_baseDF() # commented out for ONLY dev to speed up loading
# base_df.to_csv('bmeg_app/source/basedf.tsv',sep='\t',index=False) # commented out for ONLY dev to speed up loading
base_df=pd.read_csv('bmeg_app/source/basedf.tsv',sep='\t') # TEMP TODO change to cached

#######
# Page
#######
print('loading app layout')
NAME="Literature Gene-Compound Associations"
LAYOUT = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.Label('Gene Symbol'),
                        dcc.Dropdown(id='gene_dd',
                            options=[{'label': l, 'value': gid} for l,gid in lsu.gene_dd_selections(base_df,'geneID','gene').items()],
                            value=[{'label': l, 'value': gid} for l,gid in lsu.gene_dd_selections(base_df,'geneID','gene').items()][0]['value'],
                        ),
                    ],style={'width': '100%','display': 'inline-block','font-size' : styles['t']['size_font']}
                ),
            ),
        ]
    ),
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(dcc.Loading(id='occr', type="default",children=html.Div()),width=3,style={"height":"100%"}),
            dbc.Col(dcc.Loading(id='resp_histo', type="default",children=html.Div()),width=4,style={"height":"100%"}),        
            dbc.Col(dcc.Loading(id='pie_taxon', type="default",children=html.Div()),width=5,style={"height":"100%"}),     
  
        ],
    ),
    html.Hr(),
    dcc.Loading(id='evd', type="default",children=html.Div()),     
],style={'fontFamily': styles['t']['type_font']})


@app.callback(
    Output("evd", "children"),
    [Input('gene_dd', 'value')]
)
def render_callback(selected_gene):
    '''Occurance table'''
    # Filter for gene
    df = base_df[base_df['geneID']==selected_gene].reset_index(drop=True)
    # Generate table
    dictionary = lsu.parse_src_doc(df, 'litETC',['cancerType','level','drugAbstracts'])
    df = lsu.build_publication_table(dictionary)
    dashtable = dash_table.DataTable(
        id='export_pub_table',
        data = df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        page_size=10,
    )
    return dashtable,

@app.callback(
    Output("resp_histo", "children"),
    [Input('gene_dd', 'value')]
)
def render_callback(selected_gene):
    '''pie chart taxonomy'''
    # Filter for gene
    df = base_df[base_df['geneID']==selected_gene].reset_index(drop=True)
    # Generate figure
    fig= lsu.get_histogram_side(base_df['response'],main_colors['pale_yellow'])
    return html.Div(dcc.Graph(figure=fig)),

@app.callback(
    Output("pie_taxon", "children"),
    [Input('gene_dd', 'value')]
)
def render_callback(selected_gene):
    '''pie chart taxonomy'''
    # Filter for gene
    df = base_df[base_df['geneID']==selected_gene].reset_index(drop=True)
    # Generate figure
    fig= lsu.pie_from_dict(lsu.count_taxonomy(df),False)
    return html.Div(dcc.Graph(figure=fig)),

@app.callback(
    Output("occr", "children"),
    [Input('gene_dd', 'value')]
)
def render_callback(selected_gene):
    '''Occurance table'''
    # Filter for gene
    df = base_df[base_df['geneID']==selected_gene].reset_index(drop=True)
    # Generate table
    df = lsu.occurances_table(df,'drug',['Compound','Lit Occurances'])
    dashtable = dash_table.DataTable(
        id='export_pub_table',
        data = df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        page_size=10,
    )
    return dashtable,
