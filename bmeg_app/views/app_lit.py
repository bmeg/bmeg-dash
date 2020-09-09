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

######################
# Prep
######################
# Main color scheme
main_colors= ly.main_colors
styles=ly.styles

# TODO connect to figures --- Populate list of all genes for selection of 2.Drug response table 
    # TODO: cache gene_options list so can remove (below) .limit()
print('querying initial data 1')
# gene_options = lit.gene_dd_selections()
# drug_options = lit.drug_dd_selections()


# Grab baseDF for Page
# baseDF = lit.get_baseDF()
# baseDF.to_csv('bmeg_app/source/basedf.tsv',sep='\t',index=False)
baseDF=pd.read_csv('bmeg_app/source/basedf.tsv',sep='\t') # TEMP TODO change to cached
gene_options = lit.gene_dd_selections(baseDF,'geneID','gene')


##### TODO add this as a callback
card_content = [
    dbc.CardHeader("Literature Curated for Evidence Strength"),
    dbc.CardBody(
        [
            html.H5("Clinical", className="card-title"),
            html.P(lit.source_document_info(baseDF, 'litETC'),
                className="card-text",
            ),
        ]
    ),
]
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
                    multi=False,
                    ),     
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['textStyles']['size_font']}), 
            ),
            dbc.Col(html.Div([
                html.Label('Drug'),
                dcc.Dropdown(id='drug_dd',
                    # options=[
                    #     {'label': synonym, 'value': gid} for gid,synonym in drug_options.items()],
                    multi=False,
                    ),     
                ],style={'width': '100%','display': 'inline-block','font-size' : styles['textStyles']['size_font']}), 
            )
        ]),
    html.Hr(),
    html.P('Drug Response, Evidence Source, Evidence Strength (A = Strongest)'),
    dbc.Row(
        [
            dbc.Col(dbc.Card(card_content, color="info", inverse=True,style={"max-height": "28rem","overflowY": "scroll"}),width=10),
            dbc.Col(dcc.Loading(id='pie', type="default",children=html.Div(id="pie")),width=2),  
        ]
    ),
],style={'fontFamily': styles['textStyles']['type_font']})


    
    
    

# help button main
@app.callback(
    Output("main_help3", "is_open"),
    [Input("open3", "n_clicks"), Input("close3", "n_clicks")],
    [State("main_help3", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    

@app.callback(
    dash.dependencies.Output('drug_dd', 'options'),
    [dash.dependencies.Input('gene_dd', 'value')])
def set_options(selected_gene):
    return [{'label': v, 'value': k} for k,v in lit.drug_dd_selections(selected_gene, 'drugID','drug',baseDF).items()]
@app.callback(
    dash.dependencies.Output('drug_dd', 'value'),
    [dash.dependencies.Input('drug_dd', 'options')])
def set_options(available_options):
    return available_options[0]['value']    
    
    
# @app.callback(Output("figure_row1", "children"),
#     [Input('gene_dd', 'value'),
#     Input('drug_dd', 'value')])
# def render_callback(selected_gene, selected_drug):
#     # Create Piecharts 
#     subsetDF = lit.reduce_df(baseDF, 'geneID', selected_gene, 'drugID', selected_drug)
#     fig_countCard = lit.card('Gene-Drug Associations', subsetDF.shape[0],'sans-serif',200)
#     fig_pie = lit.piecharts(subsetDF)
#     # return dcc.Graph(id='pie',figure=fig_countCard), dcc.Graph(figure=fig_pie)
#     return dbc.Row([
#     dbc.Col(html.Div([dcc.Graph(id='pie',figure=fig_countCard)]),width=5),
#     dbc.Col(html.Div([dcc.Graph(figure=fig_pie)]),width=6)
#     ]),


@app.callback(Output("pie", "children"),
    [Input('gene_dd', 'value'),
    Input('drug_dd', 'value')])
def render_callback(selected_gene, selected_drug):
    # Create Piecharts 
    subsetDF = lit.reduce_df(baseDF, 'geneID', selected_gene, 'drugID', selected_drug)
    fig_pie = lit.piecharts(subsetDF)
    return html.Div(dcc.Graph(figure=fig_pie)),
    

# @app.callback(Output("gene_dd_table", "children"),
#     [Input('gene_dd', 'value')])
# def render_callback(data):
#     print(str(data) )
#     ##########
#     drug_resp = 'AAC' # TODO change from hardcoded to selection
#     ##########
# 
#     ### Query for base table ###
#     baseDF = lit.fullDF(drug_resp,data)
#     ### High Level Gene-Drug ###
#     # Table
#     tab= dash_table.DataTable(id='dropdown_table',
#         data = baseDF.to_dict('records'),columns=[{"name": i, "id": i} for i in baseDF.columns],
#         style_table={'overflowY': 'scroll', 'maxHeight':200})
# 
#     ### Detailed Gene-Drug ###
#     df2 = baseDF[['Drug Compound', 'Cell Line', 'dr_metric', 'Dataset']]
#     df2= df2.rename(columns={'dr_metric':drug_resp})
#     df2.to_csv('ignore.tsv',sep='\t',index=False)
#     # Histograms
#     drug_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Drug Compound'], 'Drug Compound', 'Frequency', main_colors['pale_orange'], 300, 200, 'drug','yes'))
#     cellLine_plot= dcc.Graph(figure=bp.get_histogram_normal(df2['Cell Line'], 'Cell Line', 'Frequency',main_colors['pale_yellow'], 300, 10, 'cellline','yes'))
#     resp_plot= dcc.Graph(figure=bp.get_histogram_normal(df2[drug_resp], drug_resp, 'Frequency',main_colors['pale_orange'], 300, 10,'drug','no'))
#     # Table
#     tab2= dash_table.DataTable(data = df2.to_dict('records'),
#         columns=[{"name": i, "id": i} for i in df2.columns],
#         style_table={'overflowY': 'scroll', 'maxHeight':200})
# 
#     # formatting figure arrangement 
#     bar_plots = dbc.Row(
#         [
#             dbc.Col(drug_plot),
#             dbc.Col(cellLine_plot),
#             dbc.Col(resp_plot),
#         ]
#     )
#     return bar_plots, tab, html.H1(''),tab2
