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
    # dcc.Loading(id="highlight_drugInfo",type="default",children=html.Div(id="card_out")),
    dcc.Loading(id="figs_repurp",type="default",children=html.Div(id="figs_repurp_out")),
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

# TODO fix drug selection to be value instead of label (update query)    
@app.callback(Output("figs_repurp", "children"),
    [Input('repurp_PROJECT_dropdown', 'value'),
    Input('repurp_RESPONSE_dropdown', 'value'),
    Input('repurp_DRUG_dropdown', 'value'),
    Input('repurp_DISEASE_dropdown','value')])
def render_age_hist(selected_project, selected_drugResp, selected_drug, selected_disease):
    # Query
    drugDF, disease = ctrt.get_matrix(selected_project,selected_drugResp)
    # Preprocess:Rename drugs to common name
    drugDF=drugDF[drugDF.columns.drop(list(drugDF.filter(regex='NO_ONTOLOGY')))] # TODO fix it so dont have to drop
    cols=drugDF.columns
    colRemap={}
    for row in G.query().V( list(cols) ).render(['$._gid', '$.synonym']):
        colRemap[row[0]] = row[1]
    common = list( colRemap[i] for i in drugDF.columns )
    drugDF.columns=common    
    # Final processing + figure violins
    finalDF,fig_violin = ctrt.compare_drugs(selected_drug, drugDF, disease,'Drug Response Metric',selected_disease )
    finalDF.to_csv('TESTING_OUTPUT.tsv',sep='\t')
    # Figure drug table
    fig_table = ctrt.drugDetails(common)
    # Cell line (pie charts and df)
    fig_CL, DF_CL=ctrt.piecharts_celllines(selected_drug,finalDF,'Project:'+selected_project)
    # format layout 
    content_cardsViolin = dbc.Row([
        dbc.Col(dcc.Loading(id="highlight_drugInfo",type="default",children=html.Div(id="card_out")),width=4),
        dbc.Col(dcc.Graph(figure=fig_violin),width=8),
    ])
    content_table = dash_table.DataTable(
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
    
    sample_celllines= dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_CL),width=5),
        dbc.Col(dash_table.DataTable(
            id='sample_char_table',
            data = DF_CL.to_dict('records'),
            columns=[{"name": i, "id": i} for i in DF_CL.columns],
            style_header={'text-align':'center','backgroundColor': 'rgb(230, 230, 230)','fontSize':styles['textStyles']['size_font'],'fontWeight': 'bold','fontFamily':styles['textStyles']['type_font']},
            style_cell={'maxWidth':'100px','padding-left': '20px','padding-right': '20px'},
            style_data={'whiteSpace':'normal','height':'auto','text-align':'center','fontFamily':styles['textStyles']['type_font'],'fontSize':styles['textStyles']['size_font']},
            style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
            style_table={'overflow':'hidden'},
            style_as_list_view=True,
            tooltip_data=[{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in DF_CL.to_dict('records')],
            tooltip_duration=None,
            export_format='xlsx',
            export_headers='display',
            page_size=5,
        ),width=7,align='center'),
    ])        

    return content_cardsViolin, html.Hr(),html.P('Drug Characteristics'),content_table,dbc.Row(html.P('Sample Characteristics')),sample_celllines,html.P('TODO add second drug selector to compare side by side and pop pie charts and table for it'),


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
