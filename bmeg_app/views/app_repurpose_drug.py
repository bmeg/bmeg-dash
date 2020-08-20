#!/usr/bin/env python

from ..app import app
from ..db import G
from ..components import func_repurpose_drug as repurpose
import pandas as pd
import time
import sys
import gripql
from collections import Counter
import plotly.express as px
import json
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from urllib.request import urlopen
import dash_core_components as dcc
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc



        
######################
# Layout
######################
# Main color scheme
main_colors = {
    'background': 'lightcyan',
    'text': 'black',
    'pale_yellow':'#FCE181',
    'pale_orange':'#F4976C',
    'lightblue':'#17BECF',
    'darkgreen_border':'#556B2F',
    'lightgreen_borderfill':'olivedrab',
    'lightgrey':'whitesmoke',
    'tab_lightblue':'#88BDBC',
    'tab_darkblue':'#026670'}

styles = {
    'section_spaced': {
        # 'border': 'thin #556B2F solid',
        'backgroundColor': main_colors['tab_lightblue'],
        'textAlign': 'center',
        # 'color':main_colors['tab_darkblue'],
        'color':'white',
        'fontSize': 15,
        'marginTop':20,
        'marginBottom':0,
        'padding':5},
    'outline': {
        'borderLeft': 'thin #556B2F solid',
        'borderRight': 'thin #556B2F solid'},
    'font_source_middle': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10,'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'font_source_bottom': {'font_family': 'sans-serif', 'textAlign':'right','fontSize':10,'padding': 10, 'borderLeft': 'thin #556B2F solid','borderRight': 'thin #556B2F solid','borderBottom': 'thin #556B2F solid','marginTop':0,'marginBottom':0},
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    },
}


########
# Page  
####### 
print('loading app layout')   
tab_layout = html.Div(children=[
    html.H4(children='Repurposing Known Breat Cancer Drugs',style=styles['section_spaced']),
    html.Label('Project'),
    html.Div([dcc.Dropdown(id='repurp_PROJECT_dropdown',
        options=[
            {'label': a, 'value': a} for a in ['CCLE']],
        value='CCLE',
        ),     
    ],style={'width': '48%', 'display': 'inline-block'}), 
    html.Label('Drug Response Metric'),
    dcc.Dropdown(id='repurp_RESPONSE_dropdown'),
    html.Label('Drug to Compare Against Others'),
    dcc.Dropdown(id='repurp_DRUG_dropdown'),

    html.Hr(),
    dbc.Button('?', id='open_repurp'),
    dbc.Modal(
        [
            dbc.ModalHeader('Header'),
            dbc.ModalBody('Desc'),
            dbc.ModalFooter(
                dbc.Button('Close',id='close_repurp',className='ml-auto')
            ),
        ],
        id='modal_repurp',
        size='sm',
        centered=True,
    ),
    # dcc.Loading(type="default",children=html.Div(id="dr_dropdown_table")),  
    dcc.Loading(id="figs_repurp",type="default",children=html.Div(id="figs_repurp_out")),
])

########
# Callbacks 
########
@app.callback(
    dash.dependencies.Output('repurp_RESPONSE_dropdown', 'options'),
    [dash.dependencies.Input('repurp_PROJECT_dropdown', 'value')])
def set_cities_options(selected_project):
    return [{'label': k, 'value': v} for k,v in repurpose.mappings_drugResp(selected_project).items()]
    
@app.callback(
    dash.dependencies.Output('repurp_RESPONSE_dropdown', 'value'),
    [dash.dependencies.Input('repurp_RESPONSE_dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']
    
    
    

@app.callback(
    dash.dependencies.Output('repurp_DRUG_dropdown', 'options'),
    [dash.dependencies.Input('repurp_PROJECT_dropdown', 'value')])
def set_cities_options(selected_project):
    return [{'label': k, 'value': v} for k,v in repurpose.mappings(selected_project).items()]
    
@app.callback(
    dash.dependencies.Output('repurp_DRUG_dropdown', 'value'),
    [dash.dependencies.Input('repurp_DRUG_dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']
    
    

@app.callback(Output("figs_repurp", "children"),
    [Input('repurp_PROJECT_dropdown', 'value'),
    Input('repurp_RESPONSE_dropdown', 'value'),
    Input('repurp_DRUG_dropdown', 'value')])
def render_age_hist(selected_project, selected_drugResp, selected_drug):
    # Query
    drugDF, disease = repurpose.get_matrix(selected_project,selected_drugResp)
    # drugDF, disease = repurpose.get_matrix('CCLE','$dr._data.aac')
    # Preprocess:Rename drugs to common name
    drugDF=drugDF[drugDF.columns.drop(list(drugDF.filter(regex='NO_ONTOLOGY')))] # TODO fix it so dont have to drop
    cols=drugDF.columns
    common=[]
    for compound in cols:
        q=G.query().V().hasLabel('Compound').has(gripql.eq('_gid',compound)).as_('c').render(['$c._data.synonym'])
        for row in q:
            common.append(row[0])
    drugDF.columns=common
    # Final processing + figure 
    fig = repurpose.compare_drugs(selected_drug, drugDF, disease,'Drug Response Metric' )[1] #grab index0 if want to do more figs from table that generates this fig
    return dcc.Graph(figure=fig),



# help button 
@app.callback(
    Output("modal_repurp", "is_open"),
    [Input("open_repurp", "n_clicks"), Input("close_repurp", "n_clicks")],
    [State("modal_repurp", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    
