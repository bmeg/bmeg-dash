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
NAME="Literature Gene-Drug Associations"
LAYOUT = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dbc.Button('Info', id='open3',color='primary',style={'font-size':styles['t']['size_font']}),
                    dbc.Modal(
                        [
                            dbc.ModalHeader('Curated Published Literature for Gene-Drug Associations'),
                            dbc.ModalBody('Explore your list of top genes from differential gene expression analysis for trends reported in literature. Quickly identify aspects about your results that align and deviate from literature curated for strength by the Variant Interpretation for Cancer Consortium.'),
                            dbc.ModalFooter(dbc.Button('Close',id='close3',className='ml-auto')),
                        ],
                        id='main_help3',
                        size='med',
                        centered=True,
                    ),
                ]),
                width=1,
            ),
            dbc.Col(html.Div([
                html.Label('Gene Symbol'),
                dcc.Dropdown(id='gene_dd',
                    options=[
                        {'label': l, 'value': gid} for l,gid in lsu.gene_dd_selections(base_df,'geneID','gene').items()],
                    value='ENSG00000198793',
                    ),
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['t']['size_font']}),
            ),
            dbc.Col(html.Div(
                [
                    html.Label('Drug'),
                    dcc.Dropdown(id='drug_dd'),
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['t']['size_font']}),
            )
        ]),
    html.Hr(),
    html.Div(id='hidden_base_df_lsu', style={'display': 'none'}),
    dcc.Loading(id='pie', type="default",children=html.Div()),
    dbc.Row(html.Button("Download", id="export_button_pub",style={'fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']}), style={'padding-left':styles['b']['padding_left'],'padding-top':styles['b']['padding_top']}),
    dcc.Loading(id='pub_table', type="default",children=html.Div()),
    dbc.Row(html.Button("Download", id="export_button_bio",style={'fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']}), style={'padding-left':styles['b']['padding_left'],'padding-top':styles['b']['padding_top']} ),
    dcc.Loading(id='bio_table', type="default",children=html.Div()),
],style={'fontFamily': styles['t']['type_font']})


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#export_pub_table button.export").click()
        return ""
    }
    """,
    Output("export_button_pub", "data-dummy"),
    [Input("export_button_pub", "n_clicks")]
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#export_bio_table button.export").click()
        return ""
    }
    """,
    Output("export_button_bio", "data-dummy"),
    [Input("export_button_bio", "n_clicks")]
)

@app.callback(Output("main_help3", "is_open"),
    [Input("open3", "n_clicks"), Input("close3", "n_clicks")],
    [State("main_help3", "is_open")])
def toggle_modal(n1, n2, is_open):
    '''main help button'''
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('drug_dd', 'options'),
    [Input('gene_dd', 'value')]
)
def set_options(selected_gene):
    '''dropdown menu - drug'''
    return [{'label': l, 'value': gid} for gid,l in lsu.drug_dd_selections(selected_gene, 'drugID','drug',base_df).items()]

@app.callback(
    Output('drug_dd', 'value'),
    [Input('drug_dd', 'options')]
)
def set_options(available_options):
    '''dropdown menu - drug'''
    return available_options[0]['value']

@app.callback(
    Output('hidden_base_df_lsu', 'children'),
    [Input('gene_dd', 'value'),
    Input('drug_dd', 'value')]
)
def createDF(selected_gene,selected_drug):
    '''Store base_df filtered for user selected gene, drug'''
    base_df_2 = lsu.reduce_df(base_df, 'geneID', selected_gene, 'drugID', selected_drug)
    return base_df_2.to_json(orient="index")

@app.callback(
    Output("pie", "children"),
    [Input('hidden_base_df_lsu', 'children')]
)
def render_callback(jsonstring):
    '''create pie charts'''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    fig_pie = lsu.piecharts(df)
    return html.Div(dcc.Graph(figure=fig_pie)),

@app.callback(
    Output("pub_table", "children"),
    [Input('hidden_base_df_lsu', 'children')]
)
def render_callback(jsonstring):
    '''publication info table'''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    res_dict = lsu.get_resultsDict(df, 'litETC')
    df2=lsu.build_publication_table(res_dict)
    fig = dash_table.DataTable(
        id='export_pub_table',
        data = df2.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df2.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df2.to_dict('records')],
        tooltip_duration=None,
        export_format='xlsx',
        export_headers='display',
        page_size=4,
    )
    return fig,

@app.callback(
    Output("bio_table", "children"),
    [Input('hidden_base_df_lsu', 'children')]
)
def render_callback(jsonstring):
    '''biological relevance info table'''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    res_dict = lsu.get_resultsDict(df, 'litETC')
    df2=lsu.build_bio_table(res_dict)
    fig = dash_table.DataTable(
        id='export_bio_table',
        data = df2.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df2.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df2.to_dict('records')],
        tooltip_duration=None,
        export_format='xlsx',
        export_headers='display',
        page_size=3,
    )
    return fig,
