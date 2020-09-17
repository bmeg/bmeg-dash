from ..app import app
from ..db import G
from ..components import compare_trt_component as ctrt
from .. import appLayout as ly
import pandas as pd
import gripql
import plotly.express as px
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import json 

# TODO format export buttons 

######################
# Prep
######################
# Main color scheme
main_colors= ly.main_colors
styles=ly.styles

#######
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dbc.Button('Info', id='open1',color='primary',style={'font-size':styles['textStyles']['size_font']}),
                    dbc.Modal(
                        [
                            dbc.ModalHeader('Identify Drugs Candidates with Similar Cell Reponses'),
                            dbc.ModalBody('Interrogate cell line drug screening trials. For example, select a FDA drug that is widely known to treat a particular disease (Paclitaxel for breast cancer treatment) and identify other drugs that show a similar impact on cell lines.'),
                            dbc.ModalBody( 'What’s going on behind the scenes?'),
                            dbc.ModalBody( '•	Data is queried from BMEG, filtered for relevant cell lines (breast tissue derived cell lines kept if breast cancer is selected), and analyzed in the viewer.'),
                            dbc.ModalBody( 'Features'),
                            dbc.ModalBody( '• Boxed in blue is a summary of the selected drug to provide insight on the molecular and/or biological realm of the selected drug.'),
                            dbc.ModalBody( '• Violin plots comparative overview: Identify alternative drugs by examining drug responses for similar distributions.'),
                            dbc.ModalBody( '• Examine the drug characteristics table for taxonomic reasons for similar and different responses from drugs.'),
                            dbc.ModalBody( '• Dive deeper to see the characteristics of the samples that generated the violin plots of particular drugs.'),
                            dbc.ModalFooter(dbc.Button('Close',id='close1',className='ml-auto')),
                        ],
                        id='main_help1',
                        size='med',
                        centered=True,
                    ),
                ]),
                width=1, 
            ),  
            dbc.Col(
                html.Div([
                    html.Label('Dataset'),
                    dcc.Dropdown(id='repurp_PROJECT_dropdown',options=[{'label': l, 'value': gid} for gid,l in ctrt.options_project().items()],value='Project:CCLE')
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['textStyles']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label('Disease'),
                    dcc.Dropdown(id='repurp_DISEASE_dropdown', value='Breast Cancer', style={'font-size' : styles['textStyles']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['textStyles']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label('Drug Treatment'),
                    dcc.Dropdown(id='repurp_DRUG_dropdown', value='Compound:CID36314', style={'font-size' : styles['textStyles']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['textStyles']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label('Drug Response Metric'),
                    dcc.Dropdown(id='repurp_RESPONSE_dropdown',style={'font-size' : styles['textStyles']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['textStyles']['size_font']})
            ),    
        ]
    ),
    html.Hr(),
    
    html.Div(id='baseDF_userSelected_ctrt', style={'display': 'none'}),


    dbc.Row([
        dbc.Col(dcc.Loading(id="highlight_drugInfo",type="default",children=html.Div(id="card_out")),width=4),  
        dbc.Col(dcc.Loading(id="violin_plot",type="default",children=html.Div(id="violin_plot_out")),width=8),
    ]),
    
    html.Hr(),
    html.P('Drug Characteristics'),
    dcc.Loading(id="drug_char_table",type="default",children=html.Div(id="drug_char_table_out")),
     
    dbc.Row(html.P('Sample Characteristics')),
    dcc.Loading(id="sample_char_table",type="default",children=html.Div(id="sample_char_table_out")),
     
],style={'fontFamily': styles['textStyles']['type_font']})


@app.callback(
    dash.dependencies.Output('repurp_RESPONSE_dropdown', 'options'),
    [dash.dependencies.Input('repurp_PROJECT_dropdown', 'value')])
def set_options(selected_project):
    return [{'label': k, 'value': v} for k,v in ctrt.mappings_drugResp(selected_project).items()]
@app.callback(
    dash.dependencies.Output('repurp_RESPONSE_dropdown', 'value'),
    [dash.dependencies.Input('repurp_RESPONSE_dropdown', 'options')])
def set_options(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('repurp_DISEASE_dropdown', 'options'),
    [dash.dependencies.Input('repurp_PROJECT_dropdown', 'value')])
def set_options(selected_project):
    return [{'label': k, 'value': k} for k in ctrt.options_disease(selected_project).keys()]

    
@app.callback(
    dash.dependencies.Output('repurp_DRUG_dropdown', 'options'),
    [dash.dependencies.Input('repurp_PROJECT_dropdown', 'value')])
def set_options(selected_project):
    return [{'label': l, 'value': gid} for gid,l in ctrt.options_drug(selected_project).items()]

@app.callback(
    dash.dependencies.Output('highlight_drugInfo', 'children'),
    [dash.dependencies.Input('repurp_DRUG_dropdown', 'value')])
def render_callback(DRUG):
    q=G.query().V(DRUG).render(['_data.synonym','_data.pubchem_id','_data.taxonomy.description'])
    for row in q:
        print('starting search')
        header = row[0].upper() + ' ('+ row[1]+')'
        descrip = row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
            html.H4(header, className="card-title",style={'fontFamily':styles['textStyles']['type_font'],'font-size' : styles['textStyles']['size_font_card'], 'fontWeight':'bold'}),
            html.P(descrip,style={'fontFamily':styles['textStyles']['type_font'],'font-size' : '12px'}) 
            ]),
        color="info", inverse=True,style={'Align': 'center', 'width':'98%','fontFamily':styles['textStyles']['type_font']})
    return fig,


@app.callback(Output('baseDF_userSelected_ctrt', 'children'), 
    [Input('repurp_PROJECT_dropdown', 'value'),
    Input('repurp_RESPONSE_dropdown', 'value'),
    Input('repurp_DRUG_dropdown','value'),
    Input('repurp_DISEASE_dropdown','value')])
def createDF(selected_project,selected_drugResp,selected_drug,selected_disease):
    '''Store intermediate df filtered for user selected project and drug response metric'''
    drugDF = ctrt.get_base_matrix(selected_project,selected_drugResp,selected_drug,selected_disease)
    print('dim of intermediate df: ', drugDF.shape)
    return drugDF.to_json(orient="index") 


@app.callback(Output("violin_plot", "children"),
    [Input('baseDF_userSelected_ctrt', 'children'),
    Input('repurp_DRUG_dropdown', 'value')])
def render_callback(jsonstring, selected_drug):
    '''create violin plot'''
    temp=json.loads(jsonstring)
    drugDF = pd.DataFrame.from_dict(temp, orient='index')
    disease_dict = ctrt.line2disease(list(drugDF.index))
    # Preprocess:Rename drugs to common name
    drugDF=drugDF[drugDF.columns.drop(list(drugDF.filter(regex='NO_ONTOLOGY')))] # TODO fix it so dont have to drop
    cols=drugDF.columns
    colRemap={}
    for row in G.query().V( list(cols) ).render(['$._gid', '$.synonym']):
        colRemap[row[0]] = row[1]
    common = list( colRemap[i] for i in drugDF.columns )
    drugDF.columns=common  
    # Create violin plots
    fig=ctrt.violins(selected_drug, ctrt.get_table(drugDF,disease_dict,'Selected Drug Response Metric'),'Drug Response Metric' )
    # format layout 
    return dcc.Graph(figure=fig),
    
        

@app.callback(Output("drug_char_table", "children"),
    [Input('baseDF_userSelected_ctrt', 'children')])
def render_callback(jsonstring):
    '''create drug characteristics table'''
    temp=json.loads(jsonstring)
    baseDF = pd.DataFrame.from_dict(temp, orient='index')
    # Preprocess:Rename drugs to common name
    df=baseDF[baseDF.columns.drop(list(baseDF.filter(regex='NO_ONTOLOGY')))]
    fig_table = ctrt.drugDetails(list(df.columns))
    table_res = dash_table.DataTable(
        id='drug_char_table',
        data = fig_table.to_dict('records'),
        columns=[{"name": i, "id": i} for i in fig_table.columns],
        style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['textStyles']['size_font'],'fontWeight': 'bold','fontFamily':styles['textStyles']['type_font']},
        style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
        style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']},
        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
        style_table={'overflow':'hidden'},
        style_as_list_view=True,
        tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in fig_table.to_dict('records')],
        tooltip_duration=None,
        export_format='xlsx',
        export_headers='display',
        page_size=5,
    )
    return table_res,
    
    
@app.callback(Output("sample_char_table", "children"),
    [Input('baseDF_userSelected_ctrt', 'children')])
def render_callback(jsonstring):
    '''create pie charts'''
    temp=json.loads(jsonstring)
    baseDF = pd.DataFrame.from_dict(temp, orient='index')
    disease_dict = ctrt.line2disease(list(baseDF.index))
    # Preprocess:Rename drugs to common name
    df2=baseDF[baseDF.columns.drop(list(baseDF.filter(regex='NO_ONTOLOGY')))] # TODO fix it so dont have to drop
    cols=df2.columns
    colRemap={}
    for row in G.query().V( list(cols) ).render(['$._gid', '$.synonym']):
        colRemap[row[0]] = row[1]
    common = list( colRemap[i] for i in df2.columns )
    df2.columns=common  
    df3 = ctrt.get_table(df2,disease_dict,'Selected Drug Response Metric')
    fig_table = ctrt.sample_table(df3)
    fig =ctrt.piecharts_celllines(df3)
    sample_celllines= dbc.Row([
        dbc.Col(dcc.Graph(figure=fig),width=5),
        dbc.Col(dash_table.DataTable(
            id='sample_char_table',
            data = fig_table.to_dict('records'),
            columns=[{"name": i, "id": i} for i in fig_table.columns],
            style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['textStyles']['size_font'],'fontWeight': 'bold','fontFamily':styles['textStyles']['type_font']},
            style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
            style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']},
            style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
            style_table={'overflow':'hidden'},
            style_as_list_view=True,
            tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in fig_table.to_dict('records')],
            tooltip_duration=None,
            export_format='xlsx',
            export_headers='display',
            page_size=5,
        ),width=7,align='center'),
    ])        
    return sample_celllines

@app.callback(
    Output("help_violin", "is_open"),
    [Input("help_violin-target", "n_clicks")],
    [State("help_violin", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open
    
# help button 
@app.callback(
    Output("main_help1", "is_open"),
    [Input("open1", "n_clicks"), Input("close1", "n_clicks")],
    [State("main_help1", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
