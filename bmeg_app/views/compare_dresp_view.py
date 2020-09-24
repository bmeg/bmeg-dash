from .. import appLayout as ly
from ..app import app
from ..components import compare_dresp_component as cdr
from ..db import G
from ..views import info_button
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
import gripql
import json 
import pandas as pd
import plotly.express as px

#######
# Prep
#######
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
                    html.Label('Dataset'),
                    dcc.Dropdown(id='project_dd_cdr',options=[{'label': l, 'value': gid} for gid,l in cdr.options_project().items()],value='Project:CCLE')
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label('Disease'),
                    dcc.Dropdown(id='disease_dd_cdr', style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']})
            ),
            dbc.Col(
                html.Div([
                    html.Label('Drug Response'),
                    dcc.Dropdown(id='dresp_dd_cdr',style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']})
            ),    
            dbc.Col(
                html.Div([
                    dbc.Button('Details', id='open1',color='primary',outline=True,style={'font-size':styles['t']['size_font']}),
                    dbc.Modal(
                        [
                            dbc.ModalHeader('Identify Drug Treatment Candidates from Cancer Cell Line Drug Screens'),
                            
                            dbc.ModalBody("Interrogate cell line drug screening trials from large established sources (CCLE, CTRP, GDSC). Dig into drug sensitivity trends within a particular disease and explore associated metadata."),
                            dbc.ModalBody( 'What’s going on behind the scenes?'),
                            dbc.ModalBody( '•	Data is queried from BMEG, filtered for relevant cell lines (breast tissue derived cell lines kept if breast cancer is selected), and analyzed in the viewer.'),
                            dbc.ModalBody( 'Panel 1 Features'),
                            dbc.ModalBody( '• Download a table of all cell line drug screening results based on three dropdown menus. Quickly see metadata composition of the table from the pie charts.'),
                            dbc.ModalBody( 'Panel 2 Features'),
                            dbc.ModalBody( '• Dive deeper to explore underlying trends between two drugs. Drug response values are plotted to quickly identify potential drug candidates that elicted similar responses from cell lines.'),
                            dbc.ModalBody( '• Blue cards provide a summary of the selected drugs to provide insight on the molecular and/or biological realm of the selected drug.'),
                            dbc.ModalBody( '• Examine the drug characteristics table for potential taxonomic reasons for similar and different responses from drugs.'),
                            dbc.ModalFooter(dbc.Button('Close',id='close1',className='ml-auto')),
                        ],
                        id='main_help1',
                        size='lg',
                        centered=True,
                    ),
                ]),
                width=1, 
            ),
        ]
    ),
    html.Hr(),
    dbc.Row(
        [
            html.Label('Drug sensitivity results from reported drug screens'),
            html.Div(info_button('help_pie','All results from selected dataset, disease, and drug response. Pie charts indicate the composition of metadata shown in table.')),
        ]
    ),
    dcc.Loading(id="sample_char_table",type="default",children=html.Div()),
     
    html.Hr(),
    dbc.Row(
        [
            html.Label('Interrogate drug screening results for drugs with similar responses'),
            html.Div(info_button('help_pair','Select two drugs from the above table to explore drug response patterns.')),
        ]
    ),
    html.Div(id='hidden_base_df_cdr', style={'display': 'none'}),
    dbc.Row([
        dbc.Col([
            html.Div(
                [
                    html.Label('Drug 1'),
                    dcc.Dropdown(id='drug_dd_cdr', style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']}
            )
        ],width=2),
        dbc.Col([
            html.Div(
                [
                    html.Label('Drug 2'),
                    dcc.Dropdown(id='drug2_dd_cdr',style={'font-size' : styles['t']['size_font']})
                ],
                style={'width': '100%', 'display': 'inline-block','font-size' : styles['t']['size_font']}
            ),
        ],width=2), 
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(id="pairwise",type="default",children=html.Div()),width=6 ),
        dbc.Col(dcc.Loading(id="drug1_box",type="default",children=html.Div()),width=3),
        dbc.Col(dcc.Loading(id="drug2_box",type="default",children=html.Div()),width=3),
    ]),
    dcc.Loading(id="drug_char_table",type="default",children=html.Div()),
],style={'fontFamily': styles['t']['type_font']})

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0)
            document.querySelector("#export_sample_table button.export").click()
        return ""
    }
    """,
    Output("export_button_sample", "data-dummy"),
    [Input("export_button_sample", "n_clicks")]
)

@app.callback(
    Output('hidden_base_df_cdr', 'children'), 
    [Input('project_dd_cdr', 'value'),
    Input('dresp_dd_cdr', 'value'),
    Input('drug_dd_cdr','value'),
    Input('disease_dd_cdr','value')]
)
def createDF(selected_project,selected_drugResp,selected_drug,selected_disease):
    '''Store intermediate df filtered for user selected project and drug response metric'''
    print(selected_project,selected_drugResp,selected_drug,selected_disease)
    df = cdr.get_base_matrix(selected_project,selected_drugResp,selected_drug,selected_disease)
    return df.to_json(orient="index") 
    
@app.callback(
    Output('dresp_dd_cdr', 'options'),
    [Input('project_dd_cdr', 'value')]
)
def set_options(selected_project):
    return [{'label': k, 'value': v} for k,v in cdr.options_dresp(selected_project).items()]
    
@app.callback(
    Output('dresp_dd_cdr', 'value'),
    [Input('dresp_dd_cdr', 'options')]
)
def set_options(available_options):
    return available_options[0]['value']

@app.callback(
    Output('disease_dd_cdr', 'options'),
    [Input('project_dd_cdr', 'value')]
)
def set_options(selected_project):
    return [{'label': k, 'value': k} for k in cdr.options_disease(selected_project)]

@app.callback(
    Output('disease_dd_cdr', 'value'),
    [Input('disease_dd_cdr', 'options')]
)
def set_options(available_options):
    return available_options[0]['value']

@app.callback(
    Output('drug_dd_cdr', 'options'),
    [Input('project_dd_cdr', 'value')]
)
def set_options(selected_project):
    return [{'label': l, 'value': gid} for gid,l in cdr.options_drug(selected_project).items()]

@app.callback(
    Output('drug_dd_cdr', 'value'),
    [Input('drug_dd_cdr', 'options')]
)
def set_options(available_options):
    return available_options[0]['value']




@app.callback(
    Output('drug2_dd_cdr', 'options'),
    [Input('hidden_base_df_cdr', 'children'),
    Input('drug_dd_cdr', 'value')]
)
def set_options(jsonstring, selected_drug):
    '''Drug2 dropdown menu options'''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    list1=list(df.columns.drop(list(df.filter(regex='NO_ONTOLOGY'))))
    if selected_drug in list1:
        list1.remove(selected_drug)
    return [{'label': l, 'value': gid} for gid,l in cdr.options_drug2(list1).items()]
    
@app.callback(
    Output('drug2_dd_cdr', 'value'),
    [Input('drug2_dd_cdr', 'options')]
)
def set_options(available_options):
    '''Default value of drug2'''
    return available_options[0]['value']
    
@app.callback(
    Output('drug1_box', 'children'),
    [Input('drug_dd_cdr', 'value')]
)
def render_callback(selected_drug):
    q=G.query().V(selected_drug).render(['_data.synonym','_data.pubchem_id','_data.taxonomy.description'])
    for row in q:
        print('starting search')
        header = row[0].upper() + ' ('+ row[1]+')'
        descrip = row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
            html.H4(header, className="card-title",style={'fontFamily':styles['t']['type_font'],'font-size' : styles['t']['size_font_card'], 'fontWeight':'bold'}),
            html.P(descrip,style={'fontFamily':styles['t']['type_font'],'font-size' : '12px'}) 
            ]),
        color="info", inverse=True,style={'Align': 'center', 'width':'98%','fontFamily':styles['t']['type_font']})
    return fig,
    
@app.callback(
    Output('drug2_box', 'children'),
    [Input('drug2_dd_cdr', 'value')]
)
def render_callback(selected_drug):
    q=G.query().V(selected_drug).render(['_data.synonym','_data.pubchem_id','_data.taxonomy.description'])
    for row in q:
        print('starting search')
        header = row[0].upper() + ' ('+ row[1]+')'
        descrip = row[2]
    fig = dbc.Card(
        dbc.CardBody(
            [
            html.H4(header, className="card-title",style={'fontFamily':styles['t']['type_font'],'font-size' : styles['t']['size_font_card'], 'fontWeight':'bold'}),
            html.P(descrip,style={'fontFamily':styles['t']['type_font'],'font-size' : '12px'}) 
            ]),
        color="info", inverse=True,style={'Align': 'center', 'width':'98%','fontFamily':styles['t']['type_font']})
    return fig,



@app.callback(
    Output("pairwise", "children"),
    [Input('hidden_base_df_cdr', 'children'),
    Input('drug_dd_cdr', 'value'),
    Input('drug2_dd_cdr', 'value'),
    Input('dresp_dd_cdr', 'value')]
)
def render_callback(jsonstring, selected_drug,selected_drug2,selected_dresp):
    '''create pairwise plots '''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    df=df[df.columns.drop(list(df.filter(regex='NO_ONTOLOGY')))]
    disease_dict = cdr.line2disease(list(df.index))
    df=cdr.get_table(df)
    fig= cdr.dresp_pairs(df,selected_drug,selected_drug2,selected_dresp) #todo add dropdown menu for section drug selection
    return dcc.Graph(figure=fig),


@app.callback(
    Output("drug_char_table", "children"),
    [Input('drug_dd_cdr', 'value'),
    Input('drug2_dd_cdr', 'value')]
)
def render_callback(selected_drug, selected_drug2):
    '''create drug characteristics table of 2 selected drugs'''
    fig_table = cdr.drugDetails([selected_drug,selected_drug2])
    table_res = dash_table.DataTable(
            id='export_drug_table',
            data = fig_table.to_dict('records'),
            columns=[{"name": i, "id": i} for i in fig_table.columns],
            style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
            style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
            style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
            style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
            style_table={'overflow':'hidden'},
            style_as_list_view=True,
            tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in fig_table.to_dict('records')],
            tooltip_duration=None,
        )
    return table_res,
    
@app.callback(
    Output("sample_char_table", "children"),
    [Input('hidden_base_df_cdr', 'children')]
)
def render_callback(jsonstring):
    '''create pie charts'''
    temp=json.loads(jsonstring)
    df = pd.DataFrame.from_dict(temp, orient='index')
    disease_dict = cdr.line2disease(list(df.index))
    df2=df[df.columns.drop(list(df.filter(regex='NO_ONTOLOGY')))]
    cols=df2.columns
    col_remap={}
    for row in G.query().V(list(cols)).render(['$._gid', '$.synonym']):
        col_remap[row[0]] = row[1]
    drug_name = list(col_remap[i] for i in df2.columns)
    df2.columns=drug_name  
    df3 = cdr.get_table(df2)
    fig_table = cdr.sample_table(df3)
    fig =cdr.piecharts_celllines(df3)
    fig_cluster= dbc.Row([
        dbc.Col(dcc.Graph(figure=fig),width=5),
        dbc.Col(
            [
                dbc.Row(html.Button("Download", id="export_button_sample",style={'fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']}), style={'padding-left':styles['b']['padding_left'],'padding-top':styles['b']['padding_top']}),
                dash_table.DataTable(
                    id='export_sample_table',
                    data = fig_table.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in fig_table.columns],
                    style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['t']['size_font'],'fontWeight': 'bold','fontFamily':styles['t']['type_font']},
                    style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
                    style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['t']['type_font'],'fontSize':styles['t']['size_font']},
                    style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
                    style_table={'overflow':'hidden'},
                    style_as_list_view=True,
                    tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in fig_table.to_dict('records')],
                    tooltip_duration=None,
                    export_format='xlsx',
                    export_headers='display',
                    page_size=8
                )
            ],width=7,align='center'
        ),
    ])        
    return fig_cluster


@app.callback(
    Output("help_violin", "is_open"),
    [Input("help_violin-target", "n_clicks")],
    [State("help_violin", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open
    
@app.callback(
    Output("main_help1", "is_open"),
    [Input("open1", "n_clicks"), Input("close1", "n_clicks")],
    [State("main_help1", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
