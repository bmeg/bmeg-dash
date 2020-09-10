from ..app import app
from ..db import G
from ..components import lit, basic_plots as bp
from .. import appLayout as ly
import pandas as pd
import gripql
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import json

######################
# Prep
######################
# Main color scheme
main_colors= ly.main_colors
styles=ly.styles

# Grab baseDF for Page (multiple genes, multi drugs)
# baseDF = lit.get_baseDF() # commented out for ONLY dev to speed up loading
# baseDF.to_csv('bmeg_app/source/basedf.tsv',sep='\t',index=False) # commented out for ONLY dev to speed up loading
baseDF=pd.read_csv('bmeg_app/source/basedf.tsv',sep='\t') # TEMP TODO change to cached
gene_options = lit.gene_dd_selections(baseDF,'geneID','gene')

########
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dbc.Button('Info', id='open3',color='primary',style={'font-size':styles['textStyles']['size_font']}),
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
                        {'label': v, 'value': k} for k,v in gene_options.items()],
                    value='ENSG00000198793',
                    ),     
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['textStyles']['size_font']}), 
            ),
            dbc.Col(html.Div(
                [
                    html.Label('Drug'),
                    dcc.Dropdown(id='drug_dd'),     
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['textStyles']['size_font']}), 
            )
        ]),
    html.Hr(),
    html.Div(id='baseDF_userSelected', style={'display': 'none'}),
    dcc.Loading(id='pie', type="default",children=html.Div(id="pie")),
    dbc.Row(html.Button("Download", id="export_button_pub",style={'fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']}), style={'padding-left':styles['buttons']['paddingleft'],'padding-top':styles['buttons']['paddingtop']}),
    dcc.Loading(id='pubTable', type="default",children=html.Div(id="pubTable")),
    dbc.Row(html.Button("Download", id="export_button_bio",style={'fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']}), style={'padding-left':styles['buttons']['paddingleft'],'padding-top':styles['buttons']['paddingtop']} ),
    dcc.Loading(id='bioTable', type="default",children=html.Div(id="bioTable")),
],style={'fontFamily': styles['textStyles']['type_font']})

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#export_pubTable button.export").click()
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
            document.querySelector("#export_pubTable button.export").click()
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
    

@app.callback(Output('drug_dd', 'options'),
    [Input('gene_dd', 'value')])
def set_options(selected_gene):
    '''dropdown menu - drug'''
    return [{'label': v, 'value': k} for k,v in lit.drug_dd_selections(selected_gene, 'drugID','drug',baseDF).items()]
@app.callback(Output('drug_dd', 'value'),
    [Input('drug_dd', 'options')])
def set_options(available_options):
    '''dropdown menu - drug'''
    return available_options[0]['value']    


@app.callback(Output('baseDF_userSelected', 'children'), 
    [Input('gene_dd', 'value'),
    Input('drug_dd', 'value')])
def createDF(selected_gene,selected_drug):
    '''Store baseDF filtered for user selected gene, drug'''
    subsetDF = lit.reduce_df(baseDF, 'geneID', selected_gene, 'drugID', selected_drug)
    return subsetDF.to_json(orient="index") 
        

@app.callback(Output("pie", "children"),
    [Input('baseDF_userSelected', 'children')])
def render_callback(jsonstring):
    '''create pie charts'''
    temp=json.loads(jsonstring)
    subsetDF = pd.DataFrame.from_dict(temp, orient='index')
    fig_pie = lit.piecharts(subsetDF)
    return html.Div(dcc.Graph(figure=fig_pie)),

@app.callback(Output("pubTable", "children"),
    [Input('baseDF_userSelected', 'children')])
def render_callback(jsonstring):
    '''publication info table'''
    temp=json.loads(jsonstring)
    subsetDF = pd.DataFrame.from_dict(temp, orient='index')
    resultsDict = lit.get_resultsDict(subsetDF, 'litETC')
    df=lit.build_publication_table(resultsDict)
    content_table = dash_table.DataTable(
        id='export_pubTable',
        data = df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['textStyles']['size_font'],'fontWeight': 'bold','fontFamily':styles['textStyles']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        export_format='xlsx',
        export_headers='display',
        page_size=4,
    )
    return content_table,    
    
    
@app.callback(Output("bioTable", "children"),
    [Input('baseDF_userSelected', 'children')])
def render_callback(jsonstring):
    '''biological relevance info table'''
    temp=json.loads(jsonstring)
    subsetDF = pd.DataFrame.from_dict(temp, orient='index')
    resultsDict = lit.get_resultsDict(subsetDF, 'litETC')
    df=lit.build_bio_table(resultsDict)
    content_table = dash_table.DataTable(
        id='export_bioTable',
        data = df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['textStyles']['size_font'],'fontWeight': 'bold','fontFamily':styles['textStyles']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in df.to_dict('records')],
        tooltip_duration=None,
        export_format='xlsx',
        export_headers='display',
        page_size=3,
    )
    return content_table,
