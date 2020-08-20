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
    html.H4(children='Repurpose Drugs',style=styles['section_spaced']),
    html.Label('Breast Cancer Drug Repurposing'),
    # html.Div([dcc.Dropdown(id='dr_dropdown',
    #     options=[
    #         {'label': g, 'value': g} for g in select_genes.keys()],
    #     value=[],
    #     multi=True,
    #     ),     
    # ],style={'width': '48%', 'display': 'inline-block'}), 
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
@app.callback(Output("figs_repurp", "children"),
    [Input('url', 'pathname')])
def render_age_hist(href):
    if href is None: # if event is trigged before page/url fully loaded
        raise PreventUpdate
    # Query
    drugDF, disease = repurpose.get_matrix('CCLE','$dr._data.aac')
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
    fig = repurpose.compare_drugs('PACLITAXEL', drugDF, disease)[1] #grab index0 if want to do more figs from table that generates this fig
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
    
